import streamlit as st
import requests

st.set_page_config(page_title="Personal Calorie Engine", layout="centered")
st.title("🍲 Personal Recipe & Batch Tracker")
st.caption("Powered by kalori-api.my 🇲🇾")

# Initialize tracking arrays with default fields
if 'ingredients' not in st.session_state:
    st.session_state.ingredients = [{"item": "", "value": 0.0, "unit": "grams", "manual_cal": 0.0}]

dish_name = st.text_input("Dish Name:", value="Chicken Curry")
st.markdown("### Ingredients Input:")

# Dropdown options matching your workflow rules
unit_options = ["grams", "KG", "quantity", "tsp", "tbsp", "ml", "L"]
total_batch_calories = 0.0

# Render our rows line-by-line
for i, ing in enumerate(st.session_state.ingredients):
    col1, col2, col3, col4 = st.columns([3, 2, 2, 2])
    
    with col1:
        ing['item'] = st.text_input(f"Item #{i+1}", value=ing['item'], placeholder="e.g., Chicken, Potato", key=f"item_{i}")
    with col2:
        ing['value'] = st.number_input("Weight/Qty", min_value=0.0, value=ing['value'], step=0.1, key=f"val_{i}")
    with col3:
        ing['unit'] = st.selectbox("Unit", options=unit_options, index=unit_options.index(ing['unit']), key=f"unit_{i}")
    
    api_calories = 0.0
    api_status_msg = ""
    
    if ing['item'].strip() and ing['value'] > 0:
        # 1. Clean query string to match Malaysian DB lookup values
        search_term = ing['item'].strip().lower()
        
        # 2. Free open public endpoint route
        api_url = f"https://api.kalori-api.my/api/v1/foods/search?query={search_term}"
        
        try:
            response = requests.get(api_url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and len(data) > 0:
                    # Target the first matching database match array element
                    matched_food = data[0]
                    # Get calories per 100g (the baseline format for the Malaysian DB)
                    cal_per_100g = float(matched_food.get('calories', 0.0))
                    
                    # 3. Handle conversion logic from user inputs dynamically
                    if ing['unit'] == "KG":
                        # 1.5 KG = 1500g -> Multiplies cal_per_100g by 15
                        api_calories = (ing['value'] * 1000 / 100) * cal_per_100g
                    elif ing['unit'] == "grams" or ing['unit'] == "ml":
                        api_calories = (ing['value'] / 100) * cal_per_100g
                    elif ing['unit'] == "L":
                        api_calories = (ing['value'] * 1000 / 100) * cal_per_100g
                    else:
                        # Baseline fallback multiplier if it's a raw generic count/quantity item
                        # Assumes a single item unit portion size averages around 100-150 grams
                        api_calories = ing['value'] * cal_per_100g
                else:
                    api_status_msg = "Not found"
            else:
                api_status_msg = f"Err {response.status_code}"
        except:
            api_status_msg = "Conn Err"

    with col4:
        # If the API hits successfully, use that value. Else, preserve user override entries.
        if api_calories > 0:
            current_val = float(api_calories)
        else:
            current_val = float(ing['manual_cal'])
            
        label_text = f"Calorie ({api_status_msg})" if api_status_msg else "Calorie (kcal)"
        
        ing['manual_cal'] = st.number_input(
            label_text, 
            min_value=0.0, 
            value=current_val, 
            step=1.0, 
            key=f"cal_{i}"
        )
    
    total_batch_calories += ing['manual_cal']

if st.button("➕ Add Ingredient Row"):
    st.session_state.ingredients.append({"item": "", "value": 0.0, "unit": "grams", "manual_cal": 0.0})
    st.rerun()

st.markdown("---")

overall_portions = st.number_input("Overall Portions:", min_value=1, value=15, step=1)
cooked_weight = st.number_input("Final Cooked Weight in Grams (Optional):", min_value=0.0, value=0.0, step=10.0)

st.markdown("### 📋 System Output:")
calories_per_serving = total_batch_calories / overall_portions

st.metric(label="Calories Overall (Whole Batch)", value=f"{int(total_batch_calories)} kcal")
st.metric(label="Calories Per Serving", value=f"{int(calories_per_serving)} kcal")

if cooked_weight > 0:
    cal_per_100g = (total_batch_calories / cooked_weight) * 100
    st.metric(label="Calories per 100g (Cooked Mass)", value=f"{int(cal_per_100g)} kcal")
else:
    st.info("💡 Cooked mass omitted. Track this item using the 'Calories Per Serving' metric inside your custom log.")
