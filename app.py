import streamlit as st
import requests

st.set_page_config(page_title="Personal Calorie Engine", layout="centered")
st.title("🍲 Personal Recipe & Batch Tracker")

# Your active API Ninjas Key
API_KEY = "3rJ5okv3gZXIkJZuZQ8Cxof7tuViayTC7yox3wJg"

# Initialize tracking arrays with default fields
if 'ingredients' not in st.session_state:
    st.session_state.ingredients = [{"item": "", "value": 0.0, "unit": "grams", "manual_cal": 0.0}]

dish_name = st.text_input("Dish Name:", value="Chicken Curry")
st.markdown("### Ingredients Input:")

# You can now use capitalizations or custom words here
unit_options = ["grams", "KG", "quantity", "tsp", "tbsp", "ml", "L"]
total_batch_calories = 0.0

# Render our rows
for i, ing in enumerate(st.session_state.ingredients):
    col1, col2, col3, col4 = st.columns([3, 2, 2, 2])
    
    with col1:
        ing['item'] = st.text_input(f"Item #{i+1}", value=ing['item'], key=f"item_{i}")
    with col2:
        ing['value'] = st.number_input("Weight/Qty", min_value=0.0, value=ing['value'], step=0.1, key=f"val_{i}")
    with col3:
        ing['unit'] = st.selectbox("Unit", options=unit_options, index=unit_options.index(ing['unit']), key=f"unit_{i}")
    
    api_calories = 0.0
    
    # Only fire network request if you actually filled something out
    if ing['item'].strip() and ing['value'] > 0:
        
        # --- SMART DATA TRANSFORMATION ARRAY LAYER ---
        # This converts your user-friendly inputs into exactly what the API database demands
        api_unit = ing['unit']
        if api_unit == "KG":
            api_unit = "kg"
        elif api_unit == "grams":
            api_unit = "g"
        elif api_unit == "quantity":
            api_unit = ""  # Leaves it blank so it reads as a raw number e.g. "6 potato"
            
        search_query = f"{ing['value']} {api_unit} {ing['item']}".strip()
        # -----------------------------------------------
        
        api_url = f"https://api.api-ninjas.com/v1/nutrition?query={search_query}"
        
        try:
            response = requests.get(api_url, headers={'X-Api-Key': API_KEY})
            if response.status_code == 200:
                data = response.json()
                api_calories = sum([item.get('calories', 0.0) for item in data])
        except:
            api_calories = 0.0

    with col4:
        # If the API hits, it auto-fills. If it returns 0, you can edit it manually.
        if api_calories > 0:
            current_val = float(api_calories)
        else:
            current_val = float(ing['manual_cal'])
            
        ing['manual_cal'] = st.number_input(
            "Calorie (kcal)", 
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
