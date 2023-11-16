import cohere
import streamlit as st
import os
import textwrap

# Cohere API key
api_key = os.getenv('COHERE_API_KEY')

# Set up Cohere client
co = cohere.Client(api_key)

def generate_recipes(ingredients, preferences, num_recipes):
    recipes = []
    for _ in range(num_recipes):
        base_recipe_prompt = textwrap.dedent(f"""
            This program generates a detailed recipe based on given ingredients and preferences.

            Ingredients: Chicken, Rice, Broccoli
            Preferences: Cuisine Type: Asian, Cooking Time: Under 45 minutes, Dietary Restrictions: None
            Recipe: Chicken and broccoli stir-fry with steamed rice.

            --
            Ingredients: {ingredients}
            Preferences: {', '.join([f'{k}: {v}' for k, v in preferences.items()])}
            Recipe: """)

        # Call the Cohere Generate endpoint
        response = co.generate(
            model='xlarge',
            prompt=base_recipe_prompt,
            max_tokens=150,
            temperature=0.7,
            k=0,
            p=0.75,
            frequency_penalty=0.5,
            presence_penalty=0,
            stop_sequences=["--"])
        recipe = response.generations[0].text
        recipe = recipe.replace("\n\n--", "").replace("\n--", "").strip()

       # Assuming the first line is the recipe name
        recipe_name = recipe.split('.')[0]

        # Format recipe name for URL
        formatted_recipe_name = '+'.join(recipe_name.split())
        
        # Append a generic recipe search link
        yummly_search_link  = f"\n\nFind similar recipes on Yummly: [Yummly Search](https://www.yummly.com/recipes?q={formatted_recipe_name}.&taste-pref-appended=true)"
        google_search_link = f"\n\nFind similar recipes on Google: [Google Search](https://www.google.com/search?q={formatted_recipe_name})"
        recipe_with_link = recipe + google_search_link + yummly_search_link
        recipes.append(recipe_with_link)

    return recipes

# Streamlit frontend code starts here
st.title("🍲 Innovative Recipe Generator")

form = st.form(key="recipe_settings")
with form:
    # User input - Ingredients
    ingredients_input = st.text_area("Enter ingredients you have (comma-separated)", key="ingredients_input")

    # Preferences
    cuisine_type_input = st.selectbox("Cuisine Type", ["Any", "Asian", "Italian", "Mexican", "Indian", "American"], key="cuisine_type_input")
    cooking_time_input = st.slider("Total Cooking Time (minutes)", min_value=10, max_value=120, value=30, key="cooking_time_input")
    dietary_restrictions_input = st.multiselect("Dietary Restrictions", ["None", "Vegetarian", "Vegan", "Gluten-Free", "Low-Carb"], key="dietary_restrictions_input")
    num_recipes_input = st.number_input("Number of Recipes to Generate", min_value=1, max_value=5, value=1, key="num_recipes_input")

    # Submit button to generate recipes
    generate_button = form.form_submit_button("Generate Recipe")

if generate_button:
    if not ingredients_input:
        st.error("Please enter some ingredients.")
    else:
        preferences = {
            "Cuisine Type": cuisine_type_input,
            "Cooking Time": f"Under {cooking_time_input} minutes",
            "Dietary Restrictions": ', '.join(dietary_restrictions_input) if dietary_restrictions_input else 'None'
        }

        recipes = generate_recipes(ingredients_input, preferences, num_recipes_input)
        st.subheader("Suggested Recipes:")
        for recipe in recipes:
            st.markdown("---")
            st.markdown(recipe, unsafe_allow_html=True)
