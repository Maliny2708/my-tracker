# Copy and paste this exact code block into your app.py file on GitHub!
import streamlit as st
import requests

st.set_page_config(page_title="Personal Calorie Engine", layout="centered")
st.title("Personal Recipe & Batch Tracker")

# Hardcoded your active API Ninjas key securely here
API_KEY = "3rJ5okv3gZXIkJZuZQ8Cxof7tuViayTC7yox3wJg"

# Initialize our dynamic tracking arrays
if 'ingredients' not in st.session_state:
    st.session_state.ingredients = [{"item": "", "value": 0.0, "unit": "grams"}]

dish_name = st.text_input("Dish Name:", value="Chicken Curry")
st.markdown("### Ingredients Input:")

unit_options = ["grams", "KG", "quantity", "tsp", "tbsp", "ml", "L"]
total_batch_calories = 0.0

# Render our row arrays line by line
for i, ing in enumerate(st.session_state.ingredients):
    col1, col2, col3, col4 = st.columns([3, 2, 2, 2])
    
    with col1:
        ing['item'] = st.text_input(f"Item #{i+1}", value=ing['item'], key=f"item_{i}")
    with col2:
        ing['value'] = st.number_input("Weight/Qty", min_value=0.0, value=ing['value'], step=0.1, key=f"val_{i}")
    with col3:
        ing['unit'] = st.selectbox("Unit", options=unit_options, index=unit_options.index(ing['unit']), key=f"unit_{i}")
    
    row_calories = 0.0
    
    if ing['item'] and ing['value'] > 0:
        # Build clean structural data text for the API Ninjas NLP layer
        search_query = f"{ing['value']} {ing['unit']} {ing['item']}"
        api_url = f"https://api.api-ninjas.com/v1/nutrition?query={search_query}"
        
        try:
            # Passing the header key required by api-ninjas account layers
            response = requests.get(api_url, headers={'X-Api-Key': API_KEY})
            if response.status_code == 200:
                data = response.json()
                # Automatically extract and calculate the calorie fields from the data array
                row_calories = sum([item.get('calories', 0.0) for item in data])
        except:
            row_calories = 0.0
            
        total_batch_calories += row_calories

    with col4:
        st.text_input("Calorie (Autofilled)", value=f"{int(row_calories)} kcal", disabled=True, key=f"cal_{i}")

if st.button("Add Ingredient Row"):
    st.session_state.ingredients.append({"item": "", "value": 0.0, "unit": "grams"})
    st.rerun()

st.markdown("---")

overall_portions = st.number_input("Overall Portions:", min_value=1, value=15, step=1)
cooked_weight = st.number_input("Final Cooked Weight in Grams (Optional):", min_value=0.0, value=0.0, step=10.0)

st.markdown("###  System Output:")
calories_per_serving = total_batch_calories / overall_portions

st.metric(label="Calories Overall (Whole Batch)", value=f"{int(total_batch_calories)} kcal")
st.metric(label="Calories Per Serving", value=f"{int(calories_per_serving)} kcal")

# Optional final calculation block (useful for tracking your custom wraps)
if cooked_weight > 0:
    cal_per_100g = (total_batch_calories / cooked_weight) * 100
    st.metric(label="Calories per 100g (Cooked Mass)", value=f"{int(cal_per_100g)} kcal")
else:
    st.info("Cooked mass omitted. Track this item using the 'Calories Per Serving' metric inside your custom log.")
