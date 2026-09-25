# # from decimal import Decimal

# # from sqlalchemy import select

# # from app.database.database import SessionLocal
# # from app.models.category import Category
# # from app.models.products import Product
# # from app.core.config import settings

# # # ============================================================================
# # # CONFIGURATION
# # # ============================================================================

# # DEMO_FARMER_ID = 1


# # # ============================================================================
# # # CATEGORY DATA
# # # ============================================================================

# # CATEGORIES = [
# #     ("Fruits", "Fresh, seasonal organic fruits."),
# #     ("Vegetables", "Farm-fresh organic vegetables."),
# #     ("Organic Oils", "Cold-pressed and unrefined organic oils."),
# #     ("Juices & Beverages", "Cold-pressed juices and organic beverages."),
# #     ("Grains & Pulses", "Organic grains, rice, and pulses."),
# #     ("Spices", "Sun-dried, chemical-free organic spices."),
# #     ("Snacks", "Healthy organic snacks and dry fruits."),
# #     ("Honey & Sweeteners", "Raw honey and natural sweeteners."),
# #     ("Personal Care", "Organic and natural personal care products."),
# # ]

# # # ============================================================================
# # # PRODUCT DATA
# # #
# # # Tuple format:
# # # (
# # #     name,
# # #     category,
# # #     price,
# # #     stock_quantity,
# # #     unit,
# # #     organic,
# # #     vendor,
# # # )
# # # ============================================================================

# # PRODUCTS = [
# #     # ========================================================================
# #     # FRUITS - 25
# #     # ========================================================================

# #     ("Alphonso Mangoes", "Fruits", 450.00, 40, "kg", True, "Konkan Organic Farms"),
# #     ("Organic Bananas", "Fruits", 60.00, 120, "dozen", True, "Demo Organic Farms"),
# #     ("Fuji Apples", "Fruits", 220.00, 75, "kg", True, "Demo Organic Farms"),
# #     ("Kashmiri Apples", "Fruits", 240.00, 65, "kg", True, "Kashmir Organic Farms"),
# #     ("Kesar Mangoes", "Fruits", 380.00, 45, "kg", True, "Gujarat Organic Farms"),
# #     ("Organic Papaya", "Fruits", 70.00, 80, "kg", True, "Demo Organic Farms"),
# #     ("Fresh Pineapple", "Fruits", 90.00, 55, "piece", True, "Kerala Organic Farms"),
# #     ("Organic Watermelon", "Fruits", 45.00, 100, "kg", True, "Demo Organic Farms"),
# #     ("Green Grapes", "Fruits", 160.00, 70, "kg", True, "Maharashtra Farms"),
# #     ("Black Grapes", "Fruits", 190.00, 55, "kg", True, "Maharashtra Farms"),
# #     ("Organic Pomegranate", "Fruits", 260.00, 60, "kg", True, "Demo Organic Farms"),
# #     ("Sweet Lime", "Fruits", 90.00, 75, "kg", True, "Andhra Organic Farms"),
# #     ("Organic Oranges", "Fruits", 110.00, 90, "kg", True, "Nagpur Organic Farms"),
# #     ("Mosambi", "Fruits", 100.00, 80, "kg", True, "Maharashtra Farms"),
# #     ("Organic Guava", "Fruits", 85.00, 70, "kg", True, "Demo Organic Farms"),
# #     ("Dragon Fruit", "Fruits", 280.00, 45, "kg", True, "Karnataka Organic Farms"),
# #     ("Organic Kiwi", "Fruits", 350.00, 40, "kg", True, "Himalayan Organic Farms"),
# #     ("Fresh Strawberries", "Fruits", 320.00, 35, "box", True, "Mahabaleshwar Farms"),
# #     ("Organic Pears", "Fruits", 240.00, 55, "kg", True, "Himachal Organic Farms"),
# #     ("Custard Apple", "Fruits", 180.00, 50, "kg", True, "Karnataka Farms"),
# #     ("Organic Sapota", "Fruits", 100.00, 65, "kg", True, "Karnataka Organic Farms"),
# #     ("Fresh Coconut", "Fruits", 55.00, 120, "piece", True, "Kerala Organic Farms"),
# #     ("Tender Coconut", "Fruits", 70.00, 100, "piece", True, "Kerala Organic Farms"),
# #     ("Organic Plums", "Fruits", 260.00, 40, "kg", True, "Himachal Organic Farms"),
# #     ("Fresh Chikoo", "Fruits", 110.00, 60, "kg", True, "Maharashtra Farms"),

# #     # ========================================================================
# #     # VEGETABLES - 30
# #     # ========================================================================

# #     ("Organic Spinach", "Vegetables", 40.00, 60, "bunch", True, "Demo Organic Farms"),
# #     ("Heirloom Tomatoes", "Vegetables", 80.00, 90, "kg", True, "Demo Organic Farms"),
# #     ("Organic Carrots", "Vegetables", 55.00, 100, "kg", True, "Demo Organic Farms"),
# #     ("Organic Potatoes", "Vegetables", 45.00, 150, "kg", True, "Demo Organic Farms"),
# #     ("Organic Onions", "Vegetables", 50.00, 140, "kg", True, "Demo Organic Farms"),
# #     ("Green Capsicum", "Vegetables", 90.00, 75, "kg", True, "Karnataka Organic Farms"),
# #     ("Red Capsicum", "Vegetables", 140.00, 60, "kg", True, "Karnataka Organic Farms"),
# #     ("Yellow Capsicum", "Vegetables", 150.00, 55, "kg", True, "Karnataka Organic Farms"),
# #     ("Organic Cucumber", "Vegetables", 50.00, 100, "kg", True, "Demo Organic Farms"),
# #     ("Organic Beetroot", "Vegetables", 60.00, 80, "kg", True, "Demo Organic Farms"),
# #     ("Fresh Broccoli", "Vegetables", 120.00, 65, "kg", True, "Ooty Organic Farms"),
# #     ("Organic Cauliflower", "Vegetables", 80.00, 70, "kg", True, "Demo Organic Farms"),
# #     ("Organic Cabbage", "Vegetables", 45.00, 90, "kg", True, "Demo Organic Farms"),
# #     ("Green Beans", "Vegetables", 100.00, 70, "kg", True, "Karnataka Organic Farms"),
# #     ("French Beans", "Vegetables", 120.00, 55, "kg", True, "Karnataka Organic Farms"),
# #     ("Organic Green Peas", "Vegetables", 140.00, 50, "kg", True, "Himachal Organic Farms"),
# #     ("Lady Finger", "Vegetables", 75.00, 80, "kg", True, "Demo Organic Farms"),
# #     ("Organic Brinjal", "Vegetables", 65.00, 90, "kg", True, "Demo Organic Farms"),
# #     ("Bottle Gourd", "Vegetables", 55.00, 70, "piece", True, "Karnataka Organic Farms"),
# #     ("Ridge Gourd", "Vegetables", 70.00, 65, "kg", True, "Karnataka Organic Farms"),
# #     ("Bitter Gourd", "Vegetables", 80.00, 60, "kg", True, "Demo Organic Farms"),
# #     ("Drumstick", "Vegetables", 110.00, 50, "kg", True, "Tamil Nadu Organic Farms"),
# #     ("Sweet Corn", "Vegetables", 60.00, 85, "piece", True, "Karnataka Organic Farms"),
# #     ("Organic Pumpkin", "Vegetables", 55.00, 60, "kg", True, "Demo Organic Farms"),
# #     ("Radish", "Vegetables", 45.00, 75, "kg", True, "Demo Organic Farms"),
# #     ("Turnip", "Vegetables", 70.00, 55, "kg", True, "Himachal Organic Farms"),
# #     ("Organic Fenugreek Leaves", "Vegetables", 35.00, 70, "bunch", True, "Demo Organic Farms"),
# #     ("Coriander Leaves", "Vegetables", 30.00, 100, "bunch", True, "Demo Organic Farms"),
# #     ("Curry Leaves", "Vegetables", 35.00, 90, "bunch", True, "Karnataka Organic Farms"),
# #     ("Organic Garlic", "Vegetables", 90.00, 80, "kg", True, "Karnataka Organic Farms"),
# #     # ========================================================================
# #     # ORGANIC OILS - 20
# #     # ========================================================================

# #     ("Cold-Pressed Coconut Oil", "Organic Oils", 320.00, 50, "litre", True, "Kerala Organic Oils"),
# #     ("Cold-Pressed Groundnut Oil", "Organic Oils", 280.00, 45, "litre", True, "Demo Organic Farms"),
# #     ("Cold-Pressed Sesame Oil", "Organic Oils", 360.00, 40, "litre", True, "Tamil Nadu Organic Farms"),
# #     ("Cold-Pressed Mustard Oil", "Organic Oils", 300.00, 45, "litre", True, "Rajasthan Organic Farms"),
# #     ("Organic Sunflower Oil", "Organic Oils", 260.00, 55, "litre", True, "Karnataka Organic Farms"),
# #     ("Organic Safflower Oil", "Organic Oils", 340.00, 35, "litre", True, "Maharashtra Farms"),
# #     ("Cold-Pressed Flaxseed Oil", "Organic Oils", 650.00, 30, "litre", True, "Himalayan Organic Farms"),
# #     ("Cold-Pressed Avocado Oil", "Organic Oils", 850.00, 25, "litre", True, "Organic Valley Farms"),
# #     ("Organic Olive Oil", "Organic Oils", 750.00, 40, "litre", True, "Indian Organic Oils"),
# #     ("Extra Virgin Olive Oil", "Organic Oils", 900.00, 30, "litre", True, "Indian Organic Oils"),
# #     ("Organic Rice Bran Oil", "Organic Oils", 290.00, 50, "litre", True, "Demo Organic Farms"),
# #     ("Cold-Pressed Walnut Oil", "Organic Oils", 780.00, 20, "litre", True, "Himachal Organic Farms"),
# #     ("Cold-Pressed Almond Oil", "Organic Oils", 950.00, 25, "litre", True, "Rajasthan Organic Farms"),
# #     ("Organic Sesame Cooking Oil", "Organic Oils", 380.00, 45, "litre", True, "Tamil Nadu Organic Farms"),
# #     ("Virgin Coconut Oil", "Organic Oils", 420.00, 40, "litre", True, "Kerala Organic Oils"),
# #     ("Organic Hemp Seed Oil", "Organic Oils", 1100.00, 15, "litre", True, "Organic Valley Farms"),
# #     ("Cold-Pressed Castor Oil", "Organic Oils", 260.00, 35, "litre", True, "Rajasthan Organic Farms"),
# #     ("Organic Moringa Oil", "Organic Oils", 900.00, 20, "litre", True, "Tamil Nadu Organic Farms"),
# #     ("Cold-Pressed Neem Oil", "Organic Oils", 350.00, 30, "litre", True, "Karnataka Organic Farms"),
# #     ("Organic Mustard Seed Oil", "Organic Oils", 310.00, 45, "litre", True, "Rajasthan Organic Farms"),

# #     # ========================================================================
# #     # JUICES & BEVERAGES - 20
# #     # ========================================================================

# #     ("Fresh Sugarcane Juice Concentrate", "Juices & Beverages", 150.00, 30, "litre", False, None),
# #     ("Organic Amla Juice", "Juices & Beverages", 180.00, 35, "litre", True, "Demo Organic Farms"),
# #     ("Organic Mango Juice", "Juices & Beverages", 220.00, 40, "litre", True, "Konkan Organic Farms"),
# #     ("Organic Orange Juice", "Juices & Beverages", 190.00, 45, "litre", True, "Nagpur Organic Farms"),
# #     ("Organic Apple Juice", "Juices & Beverages", 240.00, 35, "litre", True, "Himachal Organic Farms"),
# #     ("Organic Pomegranate Juice", "Juices & Beverages", 280.00, 30, "litre", True, "Demo Organic Farms"),
# #     ("Organic Pineapple Juice", "Juices & Beverages", 210.00, 40, "litre", True, "Kerala Organic Farms"),
# #     ("Organic Guava Juice", "Juices & Beverages", 180.00, 35, "litre", True, "Demo Organic Farms"),
# #     ("Tender Coconut Water", "Juices & Beverages", 120.00, 60, "litre", True, "Kerala Organic Farms"),
# #     ("Organic Lemon Ginger Drink", "Juices & Beverages", 160.00, 50, "litre", True, "Demo Organic Farms"),
# #     ("Organic Beetroot Juice", "Juices & Beverages", 200.00, 35, "litre", True, "Karnataka Organic Farms"),
# #     ("Organic Carrot Juice", "Juices & Beverages", 190.00, 40, "litre", True, "Demo Organic Farms"),
# #     ("Organic Mixed Fruit Juice", "Juices & Beverages", 230.00, 45, "litre", True, "Demo Organic Farms"),
# #     ("Organic Kokum Juice", "Juices & Beverages", 220.00, 30, "litre", True, "Konkan Organic Farms"),
# #     ("Organic Jamun Juice", "Juices & Beverages", 250.00, 25, "litre", True, "Karnataka Organic Farms"),
# #     ("Organic Wheatgrass Juice", "Juices & Beverages", 320.00, 20, "litre", True, "Demo Organic Farms"),
# #     ("Organic Tulsi Herbal Drink", "Juices & Beverages", 180.00, 40, "litre", True, "Demo Organic Farms"),
# #     ("Organic Cucumber Mint Juice", "Juices & Beverages", 170.00, 35, "litre", True, "Karnataka Organic Farms"),
# #     ("Organic Aloe Vera Drink", "Juices & Beverages", 200.00, 30, "litre", True, "Demo Organic Farms"),
# #     ("Organic Ginger Lemonade", "Juices & Beverages", 150.00, 50, "litre", True, "Demo Organic Farms"),

# #     # ========================================================================
# #     # GRAINS & PULSES - 25
# #     # ========================================================================

# #     ("Organic Brown Rice", "Grains & Pulses", 95.00, 200, "kg", True, "Demo Organic Farms"),
# #     ("Organic Toor Dal", "Grains & Pulses", 140.00, 150, "kg", True, "Demo Organic Farms"),
# #     ("Organic Basmati Rice", "Grains & Pulses", 180.00, 120, "kg", True, "Punjab Organic Farms"),
# #     ("Organic Sona Masoori Rice", "Grains & Pulses", 110.00, 180, "kg", True, "Karnataka Organic Farms"),
# #     ("Organic Red Rice", "Grains & Pulses", 130.00, 100, "kg", True, "Kerala Organic Farms"),
# #     ("Organic Black Rice", "Grains & Pulses", 220.00, 70, "kg", True, "Northeast Organic Farms"),
# #     ("Organic Quinoa", "Grains & Pulses", 360.00, 60, "kg", True, "Organic Valley Farms"),
# #     ("Organic Foxtail Millet", "Grains & Pulses", 140.00, 90, "kg", True, "Karnataka Organic Farms"),
# #     ("Organic Finger Millet", "Grains & Pulses", 100.00, 120, "kg", True, "Karnataka Organic Farms"),
# #     ("Organic Pearl Millet", "Grains & Pulses", 95.00, 100, "kg", True, "Rajasthan Organic Farms"),
# #     ("Organic Little Millet", "Grains & Pulses", 150.00, 70, "kg", True, "Karnataka Organic Farms"),
# #     ("Organic Kodo Millet", "Grains & Pulses", 145.00, 65, "kg", True, "Madhya Pradesh Farms"),
# #     ("Organic Barnyard Millet", "Grains & Pulses", 160.00, 60, "kg", True, "Karnataka Organic Farms"),
# #     ("Organic Green Moong Dal", "Grains & Pulses", 150.00, 120, "kg", True, "Demo Organic Farms"),
# #     ("Organic Black Urad Dal", "Grains & Pulses", 170.00, 100, "kg", True, "Demo Organic Farms"),
# #     ("Organic Chana Dal", "Grains & Pulses", 125.00, 140, "kg", True, "Rajasthan Organic Farms"),
# #     ("Organic Masoor Dal", "Grains & Pulses", 135.00, 130, "kg", True, "Madhya Pradesh Farms"),
# #     ("Organic Kabuli Chana", "Grains & Pulses", 160.00, 100, "kg", True, "Rajasthan Organic Farms"),
# #     ("Organic Rajma", "Grains & Pulses", 190.00, 90, "kg", True, "Himachal Organic Farms"),
# #     ("Organic Black Chana", "Grains & Pulses", 120.00, 110, "kg", True, "Rajasthan Organic Farms"),
# #     ("Organic Green Gram", "Grains & Pulses", 145.00, 100, "kg", True, "Karnataka Organic Farms"),
# #     ("Organic Red Kidney Beans", "Grains & Pulses", 180.00, 80, "kg", True, "Himachal Organic Farms"),
# #     ("Organic Barley", "Grains & Pulses", 90.00, 100, "kg", True, "Punjab Organic Farms"),
# #     ("Organic Rolled Oats", "Grains & Pulses", 180.00, 90, "kg", True, "Organic Valley Farms"),
# #     ("Organic Broken Wheat", "Grains & Pulses", 85.00, 120, "kg", True, "Punjab Organic Farms"),

# #     # ========================================================================
# #     # SPICES - 25
# #     # ========================================================================

# #     ("Organic Turmeric Powder", "Spices", 90.00, 80, "kg", True, "Demo Organic Farms"),
# #     ("Organic Black Pepper", "Spices", 480.00, 25, "kg", True, "Kerala Organic Oils"),
# #     ("Organic Cumin Seeds", "Spices", 360.00, 40, "kg", True, "Rajasthan Organic Farms"),
# #     ("Organic Coriander Powder", "Spices", 180.00, 55, "kg", True, "Rajasthan Organic Farms"),
# #     ("Organic Red Chilli Powder", "Spices", 220.00, 50, "kg", True, "Andhra Organic Farms"),
# #     ("Organic Green Cardamom", "Spices", 1800.00, 15, "kg", True, "Kerala Organic Farms"),
# #     ("Organic Cloves", "Spices", 1100.00, 20, "kg", True, "Kerala Organic Farms"),
# #     ("Organic Cinnamon", "Spices", 700.00, 25, "kg", True, "Kerala Organic Farms"),
# #     ("Organic Fennel Seeds", "Spices", 250.00, 35, "kg", True, "Rajasthan Organic Farms"),
# #     ("Organic Fenugreek Seeds", "Spices", 180.00, 40, "kg", True, "Rajasthan Organic Farms"),
# #     ("Organic Mustard Seeds", "Spices", 140.00, 45, "kg", True, "Rajasthan Organic Farms"),
# #     ("Organic Ajwain", "Spices", 300.00, 30, "kg", True, "Rajasthan Organic Farms"),
# #     ("Organic Bay Leaves", "Spices", 450.00, 20, "kg", True, "Kerala Organic Farms"),
# #     ("Organic Star Anise", "Spices", 900.00, 15, "kg", True, "Northeast Organic Farms"),
# #     ("Organic Nutmeg", "Spices", 1000.00, 18, "kg", True, "Kerala Organic Farms"),
# #     ("Organic Mace", "Spices", 1500.00, 12, "kg", True, "Kerala Organic Farms"),
# #     ("Organic Dry Ginger", "Spices", 380.00, 25, "kg", True, "Kerala Organic Farms"),
# #     ("Organic Asafoetida", "Spices", 1200.00, 15, "kg", True, "Demo Organic Farms"),
# #     ("Organic Garam Masala", "Spices", 300.00, 40, "kg", True, "Demo Organic Farms"),
# #     ("Organic Sambar Powder", "Spices", 280.00, 45, "kg", True, "Karnataka Organic Farms"),
# #     ("Organic Rasam Powder", "Spices", 290.00, 40, "kg", True, "Karnataka Organic Farms"),
# #     ("Organic Curry Powder", "Spices", 320.00, 35, "kg", True, "Kerala Organic Farms"),
# #     ("Organic Chaat Masala", "Spices", 280.00, 30, "kg", True, "Rajasthan Organic Farms"),
# #     ("Organic Kashmiri Chilli Powder", "Spices", 400.00, 25, "kg", True, "Kashmir Organic Farms"),
# #     ("Organic Panch Phoron", "Spices", 250.00, 30, "kg", True, "West Bengal Organic Farms"),

# #     # ========================================================================
# #     # SNACKS - 25
# #     # ========================================================================

# #     ("Roasted Makhana (Fox Nuts)", "Snacks", 260.00, 60, "kg", False, None),
# #     ("Mixed Dry Fruit Trail Mix", "Snacks", 350.00, 40, "kg", False, None),
# #     ("Organic Almonds", "Snacks", 850.00, 50, "kg", True, "Kashmir Organic Farms"),
# #     ("Organic Cashews", "Snacks", 900.00, 45, "kg", True, "Goa Organic Farms"),
# #     ("Organic Walnuts", "Snacks", 950.00, 35, "kg", True, "Kashmir Organic Farms"),
# #     ("Organic Raisins", "Snacks", 420.00, 55, "kg", True, "Maharashtra Farms"),
# #     ("Organic Dates", "Snacks", 500.00, 60, "kg", True, "Organic Valley Farms"),
# #     ("Organic Pistachios", "Snacks", 1100.00, 30, "kg", True, "Organic Valley Farms"),
# #     ("Roasted Chickpeas", "Snacks", 220.00, 70, "kg", True, "Rajasthan Organic Farms"),
# #     ("Organic Peanut Chikki", "Snacks", 280.00, 60, "kg", True, "Karnataka Organic Farms"),
# #     ("Organic Sesame Chikki", "Snacks", 300.00, 50, "kg", True, "Karnataka Organic Farms"),
# #     ("Organic Jowar Puffs", "Snacks", 180.00, 65, "kg", True, "Maharashtra Farms"),
# #     ("Organic Ragi Chips", "Snacks", 220.00, 60, "kg", True, "Karnataka Organic Farms"),
# #     ("Organic Banana Chips", "Snacks", 240.00, 70, "kg", True, "Kerala Organic Farms"),
# #     ("Organic Jackfruit Chips", "Snacks", 280.00, 50, "kg", True, "Kerala Organic Farms"),
# #     ("Organic Sweet Potato Chips", "Snacks", 260.00, 45, "kg", True, "Karnataka Organic Farms"),
# #     ("Organic Millet Cookies", "Snacks", 320.00, 50, "kg", True, "Demo Organic Farms"),
# #     ("Organic Oat Cookies", "Snacks", 300.00, 55, "kg", True, "Demo Organic Farms"),
# #     ("Organic Coconut Cookies", "Snacks", 340.00, 40, "kg", True, "Kerala Organic Farms"),
# #     ("Organic Granola", "Snacks", 450.00, 35, "kg", True, "Organic Valley Farms"),
# #     ("Organic Trail Mix", "Snacks", 500.00, 40, "kg", True, "Organic Valley Farms"),
# #     ("Roasted Pumpkin Seeds", "Snacks", 650.00, 30, "kg", True, "Organic Valley Farms"),
# #     ("Roasted Sunflower Seeds", "Snacks", 450.00, 35, "kg", True, "Organic Valley Farms"),
# #     ("Organic Coconut Chips", "Snacks", 380.00, 40, "kg", True, "Kerala Organic Farms"),
# #     ("Organic Murukku", "Snacks", 320.00, 45, "kg", True, "Karnataka Organic Farms"),

# #     # ========================================================================
# #     # HONEY & SWEETENERS - 15
# #     # ========================================================================

# #     ("Raw Forest Honey", "Honey & Sweeteners", 420.00, 55, "kg", True, "Demo Organic Farms"),
# #     ("Organic Jaggery", "Honey & Sweeteners", 85.00, 100, "kg", True, "Demo Organic Farms"),
# #     ("Organic Jaggery Powder", "Honey & Sweeteners", 110.00, 90, "kg", True, "Karnataka Organic Farms"),
# #     ("Raw Multifloral Honey", "Honey & Sweeteners", 450.00, 50, "kg", True, "Demo Organic Farms"),
# #     ("Organic Wildflower Honey", "Honey & Sweeteners", 480.00, 45, "kg", True, "Himalayan Organic Farms"),
# #     ("Organic Acacia Honey", "Honey & Sweeteners", 550.00, 35, "kg", True, "Organic Valley Farms"),
# #     ("Organic Neem Honey", "Honey & Sweeteners", 500.00, 30, "kg", True, "Karnataka Organic Farms"),
# #     ("Organic Jamun Honey", "Honey & Sweeteners", 520.00, 30, "kg", True, "Karnataka Organic Farms"),
# #     ("Organic Date Syrup", "Honey & Sweeteners", 450.00, 35, "litre", True, "Organic Valley Farms"),
# #     ("Organic Coconut Sugar", "Honey & Sweeteners", 380.00, 40, "kg", True, "Kerala Organic Farms"),
# #     ("Organic Palm Jaggery", "Honey & Sweeteners", 180.00, 60, "kg", True, "Tamil Nadu Organic Farms"),
# #     ("Organic Cane Sugar", "Honey & Sweeteners", 120.00, 80, "kg", True, "Karnataka Organic Farms"),
# #     ("Organic Stevia Powder", "Honey & Sweeteners", 650.00, 25, "kg", True, "Organic Valley Farms"),
# #     ("Organic Maple Syrup", "Honey & Sweeteners", 900.00, 25, "litre", True, "Organic Valley Farms"),
# #     ("Organic Agave Syrup", "Honey & Sweeteners", 700.00, 25, "litre", True, "Organic Valley Farms"),

# #     # ========================================================================
# #     # PERSONAL CARE - 15
# #     # ========================================================================

# #     ("Organic Aloe Vera Gel", "Personal Care", 199.00, 70, "piece", True, "Demo Organic Farms"),
# #     ("Herbal Neem Soap", "Personal Care", 60.00, 150, "piece", False, None),
# #     ("Organic Turmeric Soap", "Personal Care", 75.00, 100, "piece", True, "Demo Organic Farms"),
# #     ("Organic Sandalwood Soap", "Personal Care", 110.00, 80, "piece", True, "Karnataka Organic Farms"),
# #     ("Organic Coconut Soap", "Personal Care", 80.00, 90, "piece", True, "Kerala Organic Farms"),
# #     ("Organic Rose Face Wash", "Personal Care", 220.00, 60, "piece", True, "Demo Organic Farms"),
# #     ("Organic Neem Face Wash", "Personal Care", 210.00, 65, "piece", True, "Demo Organic Farms"),
# #     ("Organic Aloe Face Wash", "Personal Care", 230.00, 60, "piece", True, "Demo Organic Farms"),
# #     ("Organic Coconut Shampoo", "Personal Care", 280.00, 55, "piece", True, "Kerala Organic Farms"),
# #     ("Organic Hibiscus Shampoo", "Personal Care", 300.00, 50, "piece", True, "Karnataka Organic Farms"),
# #     ("Organic Amla Hair Oil", "Personal Care", 260.00, 60, "piece", True, "Demo Organic Farms"),
# #     ("Organic Coconut Hair Oil", "Personal Care", 240.00, 70, "piece", True, "Kerala Organic Farms"),
# #     ("Organic Rose Water", "Personal Care", 180.00, 75, "piece", True, "Rajasthan Organic Farms"),
# #     ("Organic Neem Powder", "Personal Care", 160.00, 50, "kg", True, "Karnataka Organic Farms"),
# #     ("Organic Multani Mitti", "Personal Care", 140.00, 60, "kg", True, "Rajasthan Organic Farms"),
# # ]


# # # ============================================================================
# # # DEMO / SEED PRODUCT IMAGES
# # #
# # # Seed images are optional. Products without a verified seed image use None.
# # # Duplicate image URLs from the previous mapping were removed.
# # # Vendor-uploaded images can replace these values later.
# # # ============================================================================

# # PRODUCT_IMAGES = {'Alphonso Mangoes': 'https://images.unsplash.com/photo-1553279768-865429fa0078?auto=format&fit=crop&w=900&q=85', 
# #                   'Organic Bananas': 'https://images.unsplash.com/photo-1571771894821-ce9b6c11b08e?auto=format&fit=crop&w=900&q=85', 
# #                   'Fuji Apples': 'https://www.saudifruit.sa/images/products-new/Fuji-Apples.jpg', 
# #                   'Kashmiri Apples': 'https://cf-img-a-in.tosshub.com/sites/visualstory/wp/2025/04/Kashmiri-ApplesITG-1745658119536.webp?size=%2A%3A900', 
# #                   'Kesar Mangoes': 'https://www.mangodatabase.com/images/varieties/whc65b65037d718f_f5QYmDjJYY_S212HU5oUr.jpg', 
# #                   'Organic Papaya': 'https://images.unsplash.com/photo-1556719240-31629484142a?auto=format&fit=crop&w=900&q=85', 
# #                   'Fresh Pineapple': 'https://upload.wikimedia.org/wikipedia/commons/9/9c/Fresh_Pineapple_Fruits.jpg', 
# #                   'Organic Watermelon': 'https://upload.wikimedia.org/wikipedia/commons/b/b9/Watermelon.jpg', 
# #                   'Green Grapes': 'https://cdn.salla.sa/apBzl/l18qeaR39amloRUWuQKfkNuBxmU79xYxhpSrWOlP.jpg', 
# #                   'Black Grapes': 'https://upload.wikimedia.org/wikipedia/commons/a/a7/Black_grapes_in_a_bowl.jpg', 
# #                   'Organic Pomegranate': 'https://tiimg.tistatic.com/fp/1/008/340/sweet-delicious-taste-natural-round-organic-pomegranate-299.jpg', 
# #                   'Sweet Lime': 'https://kfoods.com/images/glossary/479018.jpg', 
# #                   'Organic Oranges': 'https://sgwetmarket.com.sg/cdn/shop/products/2.orange-navel-313149.jpg?v=1593132715', 
# #                   'Mosambi': 'https://commons.wikimedia.org/wiki/Special:Redirect/file/(Citrus%20limetta)%20Mosambi%20at%20a%20market%20in%20Seethammadhara.jpg', 
# #                   'Organic Guava': 'https://www.agroexporters.net/uploaded-files/thumb-cache/member_127/thumb---guava_4999.jpg', 
# #                   'Dragon Fruit': 'https://img.clevup.in/278008/SKU-0195_0-1720803662130.jpg?format=webp&width=600', 
# #                   'Organic Kiwi': 'https://images.unsplash.com/photo-1539461007403-49f413d10b64?auto=format&fit=crop&w=900&q=85', 
# #                   'Fresh Strawberries': 'https://www.ars.usda.gov/ARSUserFiles/oc/images/photos/featuredphoto/aug23/D3073-1w.jpg', 
# #                   'Organic Pears': 'https://d2j6dbq0eux0bg.cloudfront.net/images/7152101/2379575823.jpg', 
# #                   'Custard Apple': 'https://pluckk.s3.ap-south-1.amazonaws.com/uploads/3153-untitled-design-61.jpg', 
# #                   'Organic Sapota': 'https://static.wixstatic.com/media/1536ae_98951bff631244c58fd8971e2857a88e~mv2.jpg/v1/fit/w_500%2Ch_500%2Cq_90/file.jpg', 
# #                   'Fresh Coconut': 'https://www.metro-online.pk/_next/image?q=75&url=https%3A%2F%2Fprodimages.metro-online.pk%2FProducts%2F1689767373521.jpg&w=3840', 'Tender Coconut': None, 'Organic Plums': 'https://i1.pickpik.com/photos/126/714/474/plum-fruit-fruits-violet-purple-preview.jpg', 
# #                   'Fresh Chikoo': 'https://services.kpnfresh.com/media/v1/products/images/09e3b8d5-2f6e-4194-955b-3f723479718e/chikoo.webp?c_type=C2', 
# #                   'Organic Spinach': 'https://images.unsplash.com/photo-1576045057995-568f588f82fb?auto=format&fit=crop&w=900&q=85',
# #                     'Heirloom Tomatoes': 'https://images.unsplash.com/photo-1546094096-0df4bcaaa337?auto=format&fit=crop&w=900&q=85',
# #                       'Organic Carrots': 'https://images.unsplash.com/photo-1445282768818-728615cc910a?auto=format&fit=crop&w=900&q=85',
# #                         'Organic Potatoes': 'https://images.unsplash.com/photo-1508313880080-c4bef0730395?auto=format&fit=crop&w=900&q=85',
# #                           'Organic Onions': 'https://www.publicdomainpictures.net/en/view-image.php?image=8303&large=1&picture=organic-onions',
# #                             'Green Capsicum': 'http://www.public-domain-image.com/full-image/flora-plants-public-domain-images-pictures/vegetables-public-domain-images-pictures/pepper-pictures/green-capsicum.jpg', 'Red Capsicum': 'https://paddocktopantry.co.nz/cdn/shop/products/redcapsicum_900x.jpg?v=1693345796', 
# #                             'Yellow Capsicum': 'https://fruitworld.co.nz/cdn/shop/products/yellow_capsicum_pepper.png?v=1606363843&width=1000', 
# #                             'Organic Cucumber': 'https://images.unsplash.com/photo-1523349462262-054f5b3aa500?auto=format&fit=crop&w=900&q=85', 
# #                             'Organic Beetroot': 'https://organicbazar.net/cdn/shop/products/Beetroot-Seeds-2.jpg?v=1694167537', 
# #                             'Fresh Broccoli': 'https://images.unsplash.com/photo-1518164147695-36c13dd568f5?auto=format&fit=crop&w=900&q=85', 
# #                             'Organic Cauliflower': 'https://images.unsplash.com/photo-1558108722-d672acd746b8?auto=format&fit=crop&w=900&q=85', 
# #                             'Organic Cabbage': 'https://superbhyper.co.za/wp-content/uploads/2023/06/CABBAGE.jpg', 'Green Beans': 
# #                             'https://www.podtatranskadebnicka.sk/application/layouts/product-images/100/100-202.jpg', 
# #                             'French Beans': 'https://dukaan.b-cdn.net/500x500/webp/4075118/f9265ecb-b431-4f32-8deb-435b516c6d0c/french-beans1-56bfad07-42eb-4e15-9d2e-acf00f34ce8a.jpg', 'Organic Green Peas': 'https://www.kibsons.com/_next/image?q=90&url=https%3A%2F%2Fcdn.kibsons.com%2Fproducts%2Fdetail%2FHPL_PEAGRPKXX04KA1_20251208115708.jpg&w=640', 
# #                             'Lady Finger': 'https://msosi.jumlajumla.com/_next/image?q=75&url=https%3A%2F%2Fmsosijumla.s3.eu-north-1.amazonaws.com%2Fpublic%2Fimages%2Fproducts%2F122-17459167781772.webp&w=3840', 
# #                             'Organic Brinjal': 'https://images.unsplash.com/photo-1647134619933-452c43b63970?auto=format&fit=crop&w=900&q=85', 
# #                             'Bottle Gourd': 'https://commons.wikimedia.org/wiki/Special:Redirect/file/Bottle%20Gourd.jpg', 
# #                             'Ridge Gourd': 'https://commons.wikimedia.org/wiki/Special:Redirect/file/Ridge%20Gourd.jpg', 
# #                             'Bitter Gourd': 'https://eshop.supernature.com.sg/cdn/shop/files/Bitter_gourd_1200x1200.jpg?v=1747106645', 
# #                             'Drumstick': 'https://toronto.motherlandgrocery.ca/cdn/shop/products/11503.png?v=1614908550', 
# #                             'Sweet Corn': 'https://www.bastanastore.com/cdn/shop/products/sweetcorn.jpg?v=1611047027', 
# #                             'Organic Pumpkin': 'https://cdn.hstatic.net/products/200000692807/bi_do_4dc1a183575040499832240426b1dc5e_master.png', 
# #                             'Radish': 'https://images.mathem.se/prod/local_products/c81f09a7-4323-4961-975f-485427b6bff8.jpg?fit=bounds&format=auto&optimize=medium&s=0xef25f48d3a4da6a2d3d1b1de87eaa5a69b099084&width=1000', 
# #                             'Turnip': None, 
# #                             'Organic Fenugreek Leaves': 'https://image.cdn.shpy.in/372001/SKU-0339_2-1730532147044.jpg?format=webp', 
# #                             'Coriander Leaves': 'https://joualvert.ca/cdn/shop/products/coriander_bb8d7913-fd8b-432e-a7b3-9e8561dbc823.jpg?v=1698701297', 
# #                             'Curry Leaves': 'https://www.asiatischer-lebensmittelladen.de/wp-content/uploads/2024/02/fresh-curry-leaves-isolated-on-600nw-1383411830.jpg.jpg', 
# #                             'Organic Garlic': 'https://untamedearth.nz/cdn/shop/products/WhatsAppImage2022-12-01at2.57.29PM_grande.jpg?v=1669860631', 
# #                             'Cold-Pressed Coconut Oil': 'https://www.bbassets.com/media/uploads/p/l/40359966_1-saffola-cold-pressed-coconut-oil.jpg', 
# #                             'Cold-Pressed Groundnut Oil': 'https://organicindia.com/cdn/shop/files/GroundnutOil1LtrBottle.png?v=1765865678&width=416', 
# #                             'Cold-Pressed Sesame Oil': 'https://excellafoods.com/cdn/shop/files/coldpresssesameoilcanvaedit.png?v=1738312913&width=500', 
# #                             'Cold-Pressed Mustard Oil': 'https://www.jiomart.com/images/product/original/494626147/saffola-cold-pressed-mustard-oil-1-l-product-images-o494626147-p612062510-0-202507301829.jpg?im=Resize%3D%281000%2C1000%29', 
# #                             'Organic Sunflower Oil': 'https://static.ah.nl/dam/product/AHI_434d50313036313232?fileType=binary&rendition=800x800_JPG_Q90&revLabel=3', 
# #                             'Organic Safflower Oil': 'https://lamoisson.com/cdn/shop/files/natur-huile-de-carthame-450ml.jpg?v=1752863776', 
# #                             'Cold-Pressed Flaxseed Oil': 'https://sunshinemarket.co.th/cdn/shop/files/Untitled-1-1.png?v=1722836486', 
# #                             'Cold-Pressed Avocado Oil': 'https://cdn.mafrservices.com/sys-master-root/ha9/hd1/35171081289758/1657615_main.jpg', 
# #                             'Organic Olive Oil': 'https://media-stark.gourmetmarketthailand.com/products/thumbnail/8859414000395-1.webp', 
# #                             'Extra Virgin Olive Oil': None, 
# #                             'Organic Rice Bran Oil': 'https://sg-live-01.slatic.net/p/f223a03b20da421a05fed6e7259a571a.jpg', 
# #                             'Cold-Pressed Walnut Oil': 'https://www.bestofhungary.co.uk/cdn/shop/files/OrganicWalnutOil250ml.jpg?v=1697444585&width=1214', 
# #                             'Cold-Pressed Almond Oil': 'https://www.niharti.com/image/cache/catalog/almond-oil-1l-700x700.jpg', 
# #                             'Organic Sesame Cooking Oil': None, 
# #                             'Virgin Coconut Oil': 'https://www.sutrakart.com/cdn/shop/files/Pure_Cold_Pressed_Virgin_Coconut_Oil.png?v=1775559484', 
# #                             'Organic Hemp Seed Oil': 'https://www.gagneensante.com/cdn/shop/products/huile-de-chanvre-biologique-624004.png?v=1762533776', 
# #                             'Cold-Pressed Castor Oil': 'https://d2j6dbq0eux0bg.cloudfront.net/images/63607701/products/624408487/5522357313.jpg', 
# #                             'Organic Moringa Oil': 'https://i5.walmartimages.com/seo/Plantlife-Moringa-Carrier-Oil-Cold-Pressed-Non-GMO-and-Gluten-Free-Carrier-Oils-For-Skin-Hair-and-Personal-Care-2-oz_eeed09fe-f279-44db-9bd8-c22382d8e897.1b97cadf537b5d072e088be8a35408da.jpeg', 
# #                             'Cold-Pressed Neem Oil': 'https://puroestadofisico.com/cdn/shop/files/Best-Naturals-Aceite-De-Neem-473ml_800x.jpg?v=1710888139', 
# #                             'Organic Mustard Seed Oil': None, 
# #                             'Fresh Sugarcane Juice Concentrate': 'https://images.unsplash.com/photo-1622597467836-f3285f2131b8?auto=format&fit=crop&w=900&q=85', 
# #                             'Organic Amla Juice': None, 'Organic Mango Juice': 'https://matjrah.online/images/1404/image/cache/catalog/1692707173-8-1100x1100.jpg', 
# #                             'Organic Orange Juice': None, 'Organic Apple Juice': 'https://dg6qn11ynnp6a.cloudfront.net/wp-content/uploads/2023/04/04105423/632856345.martinelli.s.1l.organic-scaled.jpg', 'Organic Pomegranate Juice': 'https://damassupermarket.com/2269-large_default/red-crown-organic-pomegranate-juice-1l-.jpg', 'Organic Pineapple Juice': 'https://orderacme.s3.amazonaws.com/ProductImages/00074682107340.full.jpg', 'Organic Guava Juice': None, 'Tender Coconut Water': 'https://www.pinoygrocers.com/cdn/shop/files/ee9a6f9f-1668-488e-9fd9-fe1eb6ecfe97_8906009300566_018af5f8-f51a-42d6-a15c-c4c4a49f9251.webp?v=1765823119', 
# #                             'Organic Lemon Ginger Drink': None, 'Organic Beetroot Juice': 'https://www.realfoods.co.uk/ProductImagesID/3389_1.jpg', 
# #                             'Organic Carrot Juice': 'https://cdn.salla.sa/RAxnwP/f0885e4c-bc6f-4492-9b4e-82f684698178-1000x1000-IuaL2pz135fOUnkRTrb3BnCVoKjnnie30ISxi4KL.png', 
# #                             'Organic Mixed Fruit Juice': None, 
# #                             'Organic Kokum Juice': None, 
# #                             'Organic Jamun Juice': 'https://freshmills.in/cdn/shop/files/organic-jamun-juice-867719.jpg?v=1717362174&width=1500', 
# #                             'Organic Wheatgrass Juice': 'https://vinut.com.vn/wp-content/webp-express/webp-images/uploads/2019/12/300ml_Bottled_WheatGrass_Juice_Drink_Original-600x600.jpg.webp', 
# #                             'Organic Tulsi Herbal Drink': None, 'Organic Cucumber Mint Juice': 'https://i.ebayimg.com/images/g/5PIAAOSwdsVmbP0R/s-l1200.jpg', 
# #                             'Organic Aloe Vera Drink': 'https://cdnprod.mafretailproxy.com/sys-master-root/h23/ha1/26758313803806/748853_main.jpg_480Wx480H', 
# #                             'Organic Ginger Lemonade': None, 
# #                             'Organic Brown Rice': 'https://i5.walmartimages.com/asr/b17e9da2-9904-49f2-882b-f3debd34e657_1.224a11ad9cef553c3124da53a21c821d.jpeg?odnBg=ffffff&odnHeight=1000&odnWidth=1000', 
# #                             'Organic Toor Dal': 'https://i5.walmartimages.com/seo/Sheel-Organic-Toor-Dal-Split-Pigeon-Pea-4-lbs_59d26111-dd40-44e1-bb08-aefcf7d8c87a.da1f04f304491caa1fe128aa35ca0895.jpeg?odnBg=FFFFFF&odnHeight=768&odnWidth=768', 'Organic Basmati Rice': 'https://img3.21food.com/img/product/2020/11/19/food3052421605749450953875.jpg', 'Organic Sona Masoori Rice': 'https://www.thefastrack.co.uk/uploads/products/view/1745176259.jpg', 'Organic Red Rice': 'https://www.ecohoy.com/media/catalog/product/cache/1/thumbnail/600x/9df78eab33525d08d6e5fb8d27136e95/O/r/OrganicsRedRice1Kg1800x1000.jpg', 'Organic Black Rice': 'https://i.ebayimg.com/images/g/6fsAAOSw3ZVjVWpJ/s-l1200.jpg', 'Organic Quinoa': 'https://etara-online.com/photos/shares/2022/test/20/G08-quinoa-grain-main.jpg', 'Organic Foxtail Millet': 'https://www.smartfood.org/wp-content/uploads/2020/10/foxtail-husk-off-1-930x1024.png', 'Organic Finger Millet': 'https://img.etimg.com/thumb/msid-128813492%2Cwidth-640%2Cheight-480%2Cimgsize-84604%2Cresizemode-4/finger-millet-ragi-the-iron-dense-grain.jpg', 'Organic Pearl Millet': 'https://media.post.rvohealth.io/wp-content/uploads/2020/10/bajra-pearl-millet-grain-732x549-thumbnail-732x549.jpg', 
# #                             'Organic Little Millet': 'https://bazaar5.com/image/cache/catalog/pro/product/apiData/b00pagno98-24-mantra-little-millet-500gms-pack-of-1-100-organic-chemical-free-pesticides-free-gluten-free--0-2000x2000.jpg', 'Organic Kodo Millet': 'https://cdn.shopify.com/s/files/1/2598/1404/files/Buykodomilletonline-img.webp', 
# #                             'Organic Barnyard Millet': 'https://cpimg.tistatic.com/10951881/b/4/barnyard-millet.jpg', 
# #                             'Organic Green Moong Dal': 'https://tiimg.tistatic.com/fp/1/007/562/100-percent-fresh-natural-chemical-pesticide-free-unpolished-green-moong-daal--635.jpg', 
# #                             'Organic Black Urad Dal': 'https://www.jiomart.com/images/product/600x600/rv7w6fhi8z/soni-farms-organic-unpolished-kali-urad-dal-sabut-urad-black-whole-2-kg-product-images-orv7w6fhi8z-p593790207-0-202209152122.jpg', 
# #                             'Organic Chana Dal': 'https://www.jiomart.com/images/product/original/490024261/rajdhani-chana-dal-2-kg-product-images-o490024261-p590882244-0-202506201725.jpg?im=Resize%3D%281000%2C1000%29', 
# #                             'Organic Masoor Dal': 'https://www.starquik.com/cdn/shop/files/SQ111809_FOP_910ec918-3d59-497e-8ed3-733314a5080a.jpg?v=1775027193&width=533', 
# #                             'Organic Kabuli Chana': 'https://img06.weeecdn.com/product/image/597/893/40FF56298584F3B4.jpeg', 'Organic Rajma': None, 
# #                             'Organic Black Chana': 'https://ikaiorganic.com/cdn/shop/files/Gemini_Generated_Image_r4n8wmr4n8wmr4n8.png?v=1782288840', 
# #                             'Organic Green Gram': 'https://i.ebayimg.com/images/g/hGMAAOSwr1hmblMG/s-l500.jpg', 
# #                             'Organic Red Kidney Beans': 'https://lifegid.com/media/res/1/3/9/2/1/13921.p060y0.600.jpg', 
# #                             'Organic Barley': 'https://wholefoodsbox.co.uk/cdn/shop/files/jn188.jpg?v=1719084630', 
# #                             'Organic Rolled Oats': 'https://vavapantry.com.au/cdn/shop/products/kialla-rolled-oats-organic-australia_1092c8e4-14be-4b97-a84a-7b9f46ec9fb9_1400x.png?v=1593592943', 
# #                             'Organic Broken Wheat': 'https://puretreefoods.com/cdn/shop/files/PT0084-000400BP.MAIN.jpg?v=1750417054', 
# #                             'Organic Turmeric Powder': 'https://images.unsplash.com/photo-1615485500704-8e990f9900f7?auto=format&fit=crop&w=900&q=85', 
# #                             'Organic Black Pepper': None, 'Organic Cumin Seeds': 'https://thamesorganic.com/cdn/shop/files/Organic_Cumin_Seeds_100_gr_1200x1200.jpg?v=1768397343', 
# #                             'Organic Coriander Powder': 'https://i5.walmartimages.com/seo/USDA-Organic-Coriander-Powder-4-oz-Spice-Profile-Freshly-Ground-Dhaniya-Cilantro-Molido-Lab-Tested-for-Purity_275315f5-e589-4126-b3e2-bda5f4b81bc1.9950123d7121617ed3db767e9a287d20.jpeg', 'Organic Red Chilli Powder': 'https://melionsbrothers.com/cdn/shop/files/61wxx_CyZrL._SL1080_bb5524fa-a337-4489-b794-fa8ba0ad7d22.jpg?v=1745933839&width=3840', 'Organic Green Cardamom': 'https://onsullivan.com/cdn/shop/products/76.jpg?v=1571770395', 
# #                             'Organic Cloves': 'https://i5.walmartimages.com/seo/SPICY-ORGANIC-Cloves-Whole-ESF27-100-Pure-USDA-Organic-Non-GMO-Keto-Friendly-Non-Irradiated-Fresh-Clove-Seed-Spice-4-OZ_4d385cbc-3877-47bd-a6c3-81c97ad4cea8.4e65b038b5533e241f3b14a5c53bd167.jpeg', 'Organic Cinnamon': 'https://down-my.img.susercontent.com/file/my-11134207-7r992-lv1jysjjq6go47', 'Organic Fennel Seeds': 'https://thamesorganic.com/cdn/shop/files/Organic_Fennel_Seeds_250g_1078x1078.jpg?v=1779324290', 
# #                             'Organic Fenugreek Seeds': 'https://www.jiomart.com/images/product/original/rvpmwkxpjv/24-mantra-organic-fenugreek-seeds-methi-dana-menthi-ginja-100gms-pack-of-1-100-organic-chemical-free-pesticides-free-product-images-orvpmwkxpjv-p606766671-0-202312162047.jpg?im=Resize%3D%281000%2C1000%29', 'Organic Mustard Seeds': None, 'Organic Ajwain': None, 'Organic Bay Leaves': None, 'Organic Star Anise': None, 'Organic Nutmeg': 'https://cdn.notonthehighstreet.com/fs/c3/24/316f-b54e-484e-bc80-fa3ee5d59fee/original_organic-whole-nutmeg-100g-for-cooking.jpg', 'Organic Mace': None, 
# #                             'Organic Dry Ginger': 'https://5.imimg.com/data5/SELLER/Default/2024/2/389940198/WU/MB/KB/66789684/organic-adrak-500x500.jpg', 
# #                             'Organic Asafoetida': 'https://www.lakshmiayurveda.com.au/cdn/shop/files/IMG_8725.jpg?v=1757337280&width=1200', 
# #                             'Organic Garam Masala': None, 
# #                             'Organic Sambar Powder': 'https://www.gosupps.com/media/catalog/product/cache/25/small_image/1500x1650/9df78eab33525d08d6e5fb8d27136e95/8/1/81nM6FnLDUL_2.jpg', 
# #                             'Organic Rasam Powder': None, 
# #                             'Organic Curry Powder': None, 
# #                             'Organic Chaat Masala': None, 
# #                             'Organic Kashmiri Chilli Powder': None, 
# #                             'Organic Panch Phoron': None, 
# #                             'Roasted Makhana (Fox Nuts)': 'https://healthymaster.in/cdn/shop/articles/recipe_for_makhana_chaat.jpg?v=1691743824', 
# #                             'Mixed Dry Fruit Trail Mix': 'https://www.silkrute.com/images/detailed/1951/51YteLqU0yL_kvfs-t2.jpg', 
# #                             'Organic Almonds': 'https://cdn11.bigcommerce.com/s-dis4vxtxtc/images/stencil/608x608/products/2016/5582/Organic-Almonds-1kg-Side-NUALM2.1.2__47624.1665528455.jpg?c=2', 
# #                             'Organic Cashews': 'https://m.media-amazon.com/images/I/51sGFb%2BDSML._SL1000_.jpg', 
# #                             'Organic Walnuts': 'https://cdn0.woolworths.media/content/wowproductimages/large/133476_1.jpg', 
# #                             'Organic Raisins': 'https://cdn11.bigcommerce.com/s-dis4vxtxtc/images/stencil/1280x1280/products/4941/9256/Organic-Raisins-200g-Front-DRRAI2.200__98285.1710740212.jpg?c=2%3Fimbypass%3Don', 'Organic Dates': 'https://i5.walmartimages.com/seo/Organic-California-Medjool-Dates-8-Ounces-Non-GMO-Whole-Dry-Fancy-Dates-with-Pits_c2510768-88cf-4389-8f89-4aad0967211c.dd7ddf3d21d054d4022668b272f22d94.jpeg?odnBg=FFFFFF&odnHeight=580&odnWidth=580', 'Organic Pistachios': 'https://cdn.shopaccino.com/rootzorganics/products/pistachios-5784084079764246_m.jpg?v=569', 'Roasted Chickpeas': None, 'Organic Peanut Chikki': 'https://snapcalorie-webflow-website.s3.us-east-2.amazonaws.com/media/food_pics_v2/medium/peanut_chikki.jpg', 'Organic Sesame Chikki': 'https://images.indianexpress.com/2019/01/til-chikki.jpg', 'Organic Jowar Puffs': 'https://thecowboysfarm.com/cdn/shop/files/CLASSIC_JOWAR_PUFF.jpg?v=1761809674&width=1445', 'Organic Ragi Chips': None, 'Organic Banana Chips': 'https://naturalhealthorganics.com.au/cdn/shop/products/lotus-organic-banana-chips-150g.jpg?v=1617943615', 'Organic Jackfruit Chips': 'https://archipelago-store.com/cdn/shop/files/Screenshot_2024-10-11_at_1.04.57_PM.png?v=1733347084', 'Organic Sweet Potato Chips': 'https://balevbiomarket.com/storage/26913/conversions/product_main_image_202708-thumb-620x620.webp', 'Organic Millet Cookies': 'https://www.bbassets.com/media/uploads/p/l/40301716_1-gudmom-gluten-free-millet-cookies-100-natural-jaggery.jpg', 'Organic Oat Cookies': 'https://www.organics.ph/cdn/shop/files/gullon-bio-organic-cookies-oats-250g-snacks-landers-superstore-sr-membership-shopping-979440_1024x.jpg?v=1748520607', 
# #                             'Organic Coconut Cookies': 'https://cdn.naturamarket.ca/catalog/product/cache/3c698a5d7124ca2538b36bdae68c5d8c/e/m/emmys-organics-coconut-vanilla-min.jpg', 
# #                             'Organic Granola': None, 
# #                             'Organic Trail Mix': 'https://assets.woolworths.com.au/images/1005/763844.jpg?impolicy=wowbumxfyzp', 
# #                             'Roasted Pumpkin Seeds': 'https://cupofyum.com/uploads/images/000/195/183/195183-roasted-pumpkin-seeds-perfectly-crispy-e64d628fc56cdddc85b8df745dfe8125.jpg', 
# #                             'Roasted Sunflower Seeds': 'https://www.zifiti.com/images/itemImgOrig/106/106_2357966.jpg', 
# #                             'Organic Coconut Chips': 'https://thamesorganic.com/cdn/shop/files/Coconut_Chips_100g_1024x1024.jpg?v=1768465997', 
# #                             'Organic Murukku': 'https://cdn.dotpe.in/longtail/store-items/6368205/UcYItuTz.webp', 
# #                             'Raw Forest Honey': 'https://www.bbassets.com/media/uploads/p/xl/40129245_9-natures-nectar-select-honey-forest.jpg', 
# #                             'Organic Jaggery': 'https://www.bbassets.com/media/uploads/p/l/279802_8-24-mantra-organic-jaggery.jpg', 
# #                             'Organic Jaggery Powder': 'https://pureandsure.in/cdn/shop/files/Jaggery-Powder-F_1200x1200.jpg?v=1762237438', 
# #                             'Raw Multifloral Honey': 'https://triphal.com/cdn/shop/files/Raw-Honey-by-Triphal---Pure-Best-Quality-Shahad---1.jpg?crop=center&height=800&v=1779103576&width=800', 
# #                             'Organic Wildflower Honey': 'https://www.realfoods.co.uk/ProductImagesID/44009_1.jpg', 
# #                             'Organic Acacia Honey': None, 
# #                             'Organic Neem Honey': None, 
# #                             'Organic Jamun Honey': 'https://mirchi.com/os/cdn/content/images/jamun%20honey%20shivaa%20organic_medium_0492448.webp', 
# #                             'Organic Date Syrup': 'https://datules.lt/wp-content/uploads/2024/08/Frontal-Verpackung-scaled.jpg', 
# #                             'Organic Coconut Sugar': 'https://d2lnr5mha7bycj.cloudfront.net/product-image/file/large_37ad13c1-8f6f-4091-9196-b04799c35008.png', 
# #                             'Organic Palm Jaggery': None, 
# #                             'Organic Cane Sugar': 'https://m.media-amazon.com/images/I/51xXYjecAaL._FMwebp__SR600%2C600_.jpg', 
# #                             'Organic Stevia Powder': 'https://www.novanutritions.com/cdn/shop/products/Banner3_83a3bc28-58c4-441d-91e1-32a2665b79b0_600x600.jpg?v=1681757035', 
# #                             'Organic Maple Syrup': None, 
# #                             'Organic Agave Syrup': None, 
# #                             'Organic Aloe Vera Gel': None, 
# #                             'Herbal Neem Soap': 'https://cdn11.bigcommerce.com/s-kg2w7z8739/products/28802/images/81167/M-S814__66846.1731699001.386.513.jpg?c=1', 
# #                             'Organic Turmeric Soap': 'https://pareero.com/cdn/shop/files/turmeric-organic-soap.jpg', 
# #                             'Organic Sandalwood Soap': 'https://www.rootsandmuds.com/cdn/shop/files/6298044190526_3.jpg?v=1754680303&width=533', 
# #                             'Organic Coconut Soap': 'https://phutawan.jp/cdn/shop/files/2112200002221-01.jpg?v=1770865824', 
# #                             'Organic Rose Face Wash': 'https://hnmnaturals.com/cdn/shop/files/rose-face-wash-75ml.jpg', 
# #                             'Organic Neem Face Wash': 'https://www.jiomart.com/images/product/original/rvq8ugrsex/khadi-organique-face-care-combo-rose-water-toner-neem-face-wash-pack-of-2-420-ml-product-images-orvq8ugrsex-p594285586-4-202210060813.jpg?im=Resize%3D%28420%2C420%29', 'Organic Aloe Face Wash': 'https://organicbeauty.pk/cdn/shop/files/Aloe_Vera_Face_Wash.jpg?v=1748937955', 'Organic Coconut Shampoo': 'https://www.beauty.store.bg/dcrimg/277599/bio-shampoan-s-bio-kokosovo-maslo-planeta-organica.jpg', 'Organic Hibiscus Shampoo': 'https://aorganicstore.com/cdn/shop/files/hibiscus-shampoo-pack.png?v=1771442260', 'Organic Amla Hair Oil': 'https://khadiorganique.com/cdn/shop/files/Amla02_fefb8c66-cd47-41a9-ad0a-e54ecfa489b7.jpg?v=1735208436', 'Organic Coconut Hair Oil': None, 'Organic Rose Water': 'https://www.suneetalondon.co.uk/cdn/shop/products/rosewater500ml.jpg?v=1648579971&width=1445', 'Organic Neem Powder': 'https://hennahubstore.com/cdn/shop/files/10_3_940x.jpg?v=1743674606', 'Organic Multani Mitti': 'https://organicmandyatest.myshopify.com/cdn/shop/files/Multani-Mitti-Front-100g.jpg'}

# # # ============================================================================
# # # GET PRODUCT IMAGE
# # # ============================================================================

# # def get_product_image(product_name: str, category_name: str) -> str | None:
# #     """Return the optional seed image for this exact product name."""
# #     return PRODUCT_IMAGES.get(product_name)


# # # ============================================================================
# # # SEED CATEGORIES
# # # ============================================================================

# # def seed_categories(db):

# #     category_map = {}

# #     for name, description in CATEGORIES:

# #         category = db.scalar(
# #             select(Category).where(
# #                 Category.name == name
# #             )
# #         )

# #         if category is None:

# #             category = Category(
# #                 name=name,
# #                 description=description,
# #                 is_active=True,
# #             )

# #             db.add(category)

# #             db.flush()

# #             print(
# #                 f"Created category: {name}"
# #             )

# #         else:

# #             category.description = description
# #             category.is_active = True

# #             print(
# #                 f"Category already exists: {name}"
# #             )

# #         category_map[name] = category

# #     return category_map


# # # ============================================================================
# # # SEED PRODUCTS
# # # ============================================================================

# # def seed_products(db, category_map):

# #     created = 0
# #     updated = 0
# #     image_count = 0
# #     missing_images = []

# #     for (
# #         name,
# #         category_name,
# #         price,
# #         stock_quantity,
# #         unit,
# #         organic,
# #         vendor,
# #     ) in PRODUCTS:

# #         # --------------------------------------------------------------------
# #         # Validate category
# #         # --------------------------------------------------------------------

# #         if category_name not in category_map:

# #             raise ValueError(
# #                 f"Unknown category '{category_name}' "
# #                 f"for product '{name}'"
# #             )

# #         category = category_map[category_name]

# #         # --------------------------------------------------------------------
# #         # Check existing product
# #         # --------------------------------------------------------------------

# #         product = db.scalar(
# #             select(Product).where(
# #                 Product.seller_id == DEMO_FARMER_ID,
# #                 Product.name == name,
# #             )
# #         )

# #         # --------------------------------------------------------------------
# #         # IMPORTANT:
# #         #
# #         # If an existing product already has an image, keep it.
# #         # Otherwise find a product-specific image.
# #         # --------------------------------------------------------------------

# #         if product is not None and product.image_url:

# #             image_url = product.image_url

# #             print(
# #                 f"Using existing image: {name}"
# #             )

# #         else:

# #             image_url = get_product_image(
# #                 product_name=name,
# #                 category_name=category_name,
# #             )

# #         # --------------------------------------------------------------------
# #         # Image status
# #         # --------------------------------------------------------------------

# #         if image_url:

# #             image_count += 1

# #             print(
# #                 f"Image assigned: {name}"
# #             )

# #         else:

# #             missing_images.append(name)

# #             print(
# #                 f"WARNING: No image found: {name}"
# #             )

# #         # --------------------------------------------------------------------
# #         # Product description
# #         # --------------------------------------------------------------------

# #         description = (
# #             f"{'Organic' if organic else 'Natural'} "
# #             f"{name}."
# #         )

# #         # --------------------------------------------------------------------
# #         # CREATE
# #         # --------------------------------------------------------------------

# #         if product is None:

# #             product = Product(
# #                 seller_id=DEMO_FARMER_ID,
# #                 category_id=category.id,
# #                 name=name,
# #                 description=description,
# #                 price=Decimal(str(price)),
# #                 stock_quantity=stock_quantity,
# #                 unit=unit,
# #                 certification="APPROVED",
# #                 image_url=image_url,
# #                 is_active=True,
# #             )

# #             db.add(product)

# #             created += 1

# #             print(
# #                 f"Created product: {name}"
# #             )

# #         # --------------------------------------------------------------------
# #         # UPDATE
# #         # --------------------------------------------------------------------

# #         else:

# #             product.category_id = category.id
# #             product.description = description
# #             product.price = Decimal(str(price))
# #             product.stock_quantity = stock_quantity
# #             product.unit = unit
# #             product.certification = "APPROVED"
# #             product.is_active = True

# #             # Only replace image if we successfully found one.
# #             if image_url:
# #                 product.image_url = image_url

# #             updated += 1

# #             print(
# #                 f"Updated product: {name}"
# #             )

# #     return (
# #         created,
# #         updated,
# #         image_count,
# #         missing_images,
# #     )


# # # ============================================================================
# # # VALIDATION
# # # ============================================================================

# # def validate_catalog():

# #     product_count = len(PRODUCTS)

# #     category_count = len(CATEGORIES)

# #     print()
# #     print("=" * 70)
# #     print("CATALOG VALIDATION")
# #     print("=" * 70)

# #     print(
# #         f"Categories defined : {category_count}"
# #     )

# #     print(
# #         f"Products defined   : {product_count}"
# #     )

# #     if category_count != 9:

# #         raise ValueError(
# #             f"Expected 9 categories, "
# #             f"found {category_count}"
# #         )

# #     if product_count != 200:

# #         raise ValueError(
# #             f"Expected exactly 200 products, "
# #             f"found {product_count}"
# #         )

# #     # ------------------------------------------------------------------------
# #     # Validate product categories
# #     # ------------------------------------------------------------------------

# #     valid_categories = {
# #         name for name, _ in CATEGORIES
# #     }

# #     invalid_products = [
# #         (
# #             name,
# #             category_name,
# #         )
# #         for (
# #             name,
# #             category_name,
# #             price,
# #             stock,
# #             unit,
# #             organic,
# #             vendor,
# #         ) in PRODUCTS
# #         if category_name not in valid_categories
# #     ]

# #     if invalid_products:

# #         print("\nInvalid products:")

# #         for name, category_name in invalid_products:

# #             print(
# #                 f"  {name} -> {category_name}"
# #             )

# #         raise ValueError(
# #             "One or more products contain "
# #             "invalid categories."
# #         )

# #     # ------------------------------------------------------------------------
# #     # Check duplicate product names
# #     # ------------------------------------------------------------------------

# #     names = [
# #         product[0]
# #         for product in PRODUCTS
# #     ]

# #     duplicates = {
# #         name
# #         for name in names
# #         if names.count(name) > 1
# #     }

# #     if duplicates:

# #         raise ValueError(
# #             "Duplicate product names found: "
# #             + ", ".join(sorted(duplicates))
# #         )

# #     print()
# #     print("Catalog validation passed.")
# #     print("=" * 70)


# # # ============================================================================
# # # IMAGE VALIDATION
# # # ============================================================================

# # def validate_product_images():
# #     """Validate image mappings while allowing missing images (None)."""
# #     product_names = {product[0] for product in PRODUCTS}
# #     mapped_names = set(PRODUCT_IMAGES)

# #     if mapped_names != product_names:
# #         missing = sorted(product_names - mapped_names)
# #         extra = sorted(mapped_names - product_names)
# #         raise ValueError(f"Image mapping mismatch. Missing: {missing}; Extra: {extra}")

# #     urls = [url for url in PRODUCT_IMAGES.values() if url]
# #     duplicates = {url for url in urls if urls.count(url) > 1}
# #     if duplicates:
# #         raise ValueError("Duplicate non-null product image URLs detected:\n" + "\n".join(sorted(duplicates)))

# #     print(f"Image mappings defined : {len(PRODUCT_IMAGES)}")
# #     print(f"Unique seed image URLs : {len(urls)}")
# #     print(f"Products with no image : {len(PRODUCT_IMAGES) - len(urls)}")
# #     print("Image mapping validation passed.")


# # # ============================================================================
# # # MAIN
# # # ============================================================================

# # def main():

# #     print("=" * 70)
# #     print("OrganicKart Product Catalog Seed")
# #     print("=" * 70)

# #     # ------------------------------------------------------------------------
# #     # Validate the hardcoded catalog BEFORE touching the database.
# #     # ------------------------------------------------------------------------

# #     validate_catalog()
# #     validate_product_images()

# #     # ------------------------------------------------------------------------
# #     # Database session
# #     # ------------------------------------------------------------------------

# #     db = SessionLocal()

# #     try:

# #         # --------------------------------------------------------------------
# #         # Categories
# #         # --------------------------------------------------------------------

# #         print()
# #         print("Seeding categories...")

# #         category_map = seed_categories(db)

# #         # --------------------------------------------------------------------
# #         # Products
# #         # --------------------------------------------------------------------

# #         print()
# #         print("Seeding products...")

# #         (
# #             created,
# #             updated,
# #             image_count,
# #             missing_images,
# #         ) = seed_products(
# #             db,
# #             category_map,
# #         )

# #         # --------------------------------------------------------------------
# #         # Commit
# #         # --------------------------------------------------------------------

# #         db.commit()

# #         # --------------------------------------------------------------------
# #         # Summary
# #         # --------------------------------------------------------------------

# #         print()
# #         print("=" * 70)
# #         print("SEED COMPLETE")
# #         print("=" * 70)

# #         print(
# #             f"Categories          : {len(category_map)}"
# #         )

# #         print(
# #             f"Products defined    : {len(PRODUCTS)}"
# #         )

# #         print(
# #             f"Products created    : {created}"
# #         )

# #         print(
# #             f"Products updated    : {updated}"
# #         )

# #         print(
# #             f"Images assigned     : {image_count}"
# #         )

# #         print(
# #             f"Images missing      : {len(missing_images)}"
# #         )

# #         print(
# #             f"Seller ID           : {DEMO_FARMER_ID}"
# #         )

# #         # --------------------------------------------------------------------
# #         # Missing images
# #         # --------------------------------------------------------------------

# #         if missing_images:

# #             print()
# #             print("Products without images:")

# #             for product_name in missing_images:

# #                 print(
# #                     f"  - {product_name}"
# #                 )

# #         else:

# #             print()
# #             print(
# #                 "SUCCESS: Seed image URLs are unique; products without images are ready for vendor upload."
# #             )

# #         print("=" * 70)

# #     except Exception:

# #         db.rollback()

# #         raise

# #     finally:

# #         db.close()


# # # ============================================================================
# # # ENTRY POINT
# # # ============================================================================

# # if __name__ == "__main__":
# #     main()

# from decimal import Decimal

# from sqlalchemy import select

# from app.database.database import SessionLocal
# from app.models.category import Category
# from app.models.products import Product
# from app.core.config import settings

# # ============================================================================
# # CONFIGURATION
# # ============================================================================

# DEMO_FARMER_ID = 1


# # ============================================================================
# # CATEGORY DATA
# # ============================================================================

# CATEGORIES = [
#     ("Fruits", "Fresh, seasonal organic fruits."),
#     ("Vegetables", "Farm-fresh organic vegetables."),
#     ("Organic Oils", "Cold-pressed and unrefined organic oils."),
#     ("Juices & Beverages", "Cold-pressed juices and organic beverages."),
#     ("Grains & Pulses", "Organic grains, rice, and pulses."),
#     ("Spices", "Sun-dried, chemical-free organic spices."),
#     ("Snacks", "Healthy organic snacks and dry fruits."),
#     ("Honey & Sweeteners", "Raw honey and natural sweeteners."),
#     ("Personal Care", "Organic and natural personal care products."),
# ]

# # ============================================================================
# # PRODUCT DATA
# #
# # Tuple format:
# # (
# #     name,
# #     category,
# #     price,
# #     stock_quantity,
# #     unit,
# #     organic,
# #     vendor,
# # )
# # ============================================================================

# PRODUCTS = [
#     # ========================================================================
#     # FRUITS - 25
#     # ========================================================================

#     ("Alphonso Mangoes", "Fruits", 450.00, 40, "kg", True, "Konkan Organic Farms"),
#     ("Organic Bananas", "Fruits", 60.00, 120, "dozen", True, "Demo Organic Farms"),
#     ("Fuji Apples", "Fruits", 220.00, 75, "kg", True, "Demo Organic Farms"),
#     ("Kashmiri Apples", "Fruits", 240.00, 65, "kg", True, "Kashmir Organic Farms"),
#     ("Kesar Mangoes", "Fruits", 380.00, 45, "kg", True, "Gujarat Organic Farms"),
#     ("Organic Papaya", "Fruits", 70.00, 80, "kg", True, "Demo Organic Farms"),
#     ("Fresh Pineapple", "Fruits", 90.00, 55, "piece", True, "Kerala Organic Farms"),
#     ("Organic Watermelon", "Fruits", 45.00, 100, "kg", True, "Demo Organic Farms"),
#     ("Green Grapes", "Fruits", 160.00, 70, "kg", True, "Maharashtra Farms"),
#     ("Black Grapes", "Fruits", 190.00, 55, "kg", True, "Maharashtra Farms"),
#     ("Organic Pomegranate", "Fruits", 260.00, 60, "kg", True, "Demo Organic Farms"),
#     ("Sweet Lime", "Fruits", 90.00, 75, "kg", True, "Andhra Organic Farms"),
#     ("Organic Oranges", "Fruits", 110.00, 90, "kg", True, "Nagpur Organic Farms"),
#     ("Mosambi", "Fruits", 100.00, 80, "kg", True, "Maharashtra Farms"),
#     ("Organic Guava", "Fruits", 85.00, 70, "kg", True, "Demo Organic Farms"),
#     ("Dragon Fruit", "Fruits", 280.00, 45, "kg", True, "Karnataka Organic Farms"),
#     ("Organic Kiwi", "Fruits", 350.00, 40, "kg", True, "Himalayan Organic Farms"),
#     ("Fresh Strawberries", "Fruits", 320.00, 35, "box", True, "Mahabaleshwar Farms"),
#     ("Organic Pears", "Fruits", 240.00, 55, "kg", True, "Himachal Organic Farms"),
#     ("Custard Apple", "Fruits", 180.00, 50, "kg", True, "Karnataka Farms"),
#     ("Organic Sapota", "Fruits", 100.00, 65, "kg", True, "Karnataka Organic Farms"),
#     ("Fresh Coconut", "Fruits", 55.00, 120, "piece", True, "Kerala Organic Farms"),
#     ("Tender Coconut", "Fruits", 70.00, 100, "piece", True, "Kerala Organic Farms"),
#     ("Organic Plums", "Fruits", 260.00, 40, "kg", True, "Himachal Organic Farms"),
#     ("Fresh Chikoo", "Fruits", 110.00, 60, "kg", True, "Maharashtra Farms"),

#     # ========================================================================
#     # VEGETABLES - 30
#     # ========================================================================

#     ("Organic Spinach", "Vegetables", 40.00, 60, "bunch", True, "Demo Organic Farms"),
#     ("Heirloom Tomatoes", "Vegetables", 80.00, 90, "kg", True, "Demo Organic Farms"),
#     ("Organic Carrots", "Vegetables", 55.00, 100, "kg", True, "Demo Organic Farms"),
#     ("Organic Potatoes", "Vegetables", 45.00, 150, "kg", True, "Demo Organic Farms"),
#     ("Organic Onions", "Vegetables", 50.00, 140, "kg", True, "Demo Organic Farms"),
#     ("Green Capsicum", "Vegetables", 90.00, 75, "kg", True, "Karnataka Organic Farms"),
#     ("Red Capsicum", "Vegetables", 140.00, 60, "kg", True, "Karnataka Organic Farms"),
#     ("Yellow Capsicum", "Vegetables", 150.00, 55, "kg", True, "Karnataka Organic Farms"),
#     ("Organic Cucumber", "Vegetables", 50.00, 100, "kg", True, "Demo Organic Farms"),
#     ("Organic Beetroot", "Vegetables", 60.00, 80, "kg", True, "Demo Organic Farms"),
#     ("Fresh Broccoli", "Vegetables", 120.00, 65, "kg", True, "Ooty Organic Farms"),
#     ("Organic Cauliflower", "Vegetables", 80.00, 70, "kg", True, "Demo Organic Farms"),
#     ("Organic Cabbage", "Vegetables", 45.00, 90, "kg", True, "Demo Organic Farms"),
#     ("Green Beans", "Vegetables", 100.00, 70, "kg", True, "Karnataka Organic Farms"),
#     ("French Beans", "Vegetables", 120.00, 55, "kg", True, "Karnataka Organic Farms"),
#     ("Organic Green Peas", "Vegetables", 140.00, 50, "kg", True, "Himachal Organic Farms"),
#     ("Lady Finger", "Vegetables", 75.00, 80, "kg", True, "Demo Organic Farms"),
#     ("Organic Brinjal", "Vegetables", 65.00, 90, "kg", True, "Demo Organic Farms"),
#     ("Bottle Gourd", "Vegetables", 55.00, 70, "piece", True, "Karnataka Organic Farms"),
#     ("Ridge Gourd", "Vegetables", 70.00, 65, "kg", True, "Karnataka Organic Farms"),
#     ("Bitter Gourd", "Vegetables", 80.00, 60, "kg", True, "Demo Organic Farms"),
#     ("Drumstick", "Vegetables", 110.00, 50, "kg", True, "Tamil Nadu Organic Farms"),
#     ("Sweet Corn", "Vegetables", 60.00, 85, "piece", True, "Karnataka Organic Farms"),
#     ("Organic Pumpkin", "Vegetables", 55.00, 60, "kg", True, "Demo Organic Farms"),
#     ("Radish", "Vegetables", 45.00, 75, "kg", True, "Demo Organic Farms"),
#     ("Turnip", "Vegetables", 70.00, 55, "kg", True, "Himachal Organic Farms"),
#     ("Organic Fenugreek Leaves", "Vegetables", 35.00, 70, "bunch", True, "Demo Organic Farms"),
#     ("Coriander Leaves", "Vegetables", 30.00, 100, "bunch", True, "Demo Organic Farms"),
#     ("Curry Leaves", "Vegetables", 35.00, 90, "bunch", True, "Karnataka Organic Farms"),
#     ("Organic Garlic", "Vegetables", 90.00, 80, "kg", True, "Karnataka Organic Farms"),
#     # ========================================================================
#     # ORGANIC OILS - 20
#     # ========================================================================

#     ("Cold-Pressed Coconut Oil", "Organic Oils", 320.00, 50, "litre", True, "Kerala Organic Oils"),
#     ("Cold-Pressed Groundnut Oil", "Organic Oils", 280.00, 45, "litre", True, "Demo Organic Farms"),
#     ("Cold-Pressed Sesame Oil", "Organic Oils", 360.00, 40, "litre", True, "Tamil Nadu Organic Farms"),
#     ("Cold-Pressed Mustard Oil", "Organic Oils", 300.00, 45, "litre", True, "Rajasthan Organic Farms"),
#     ("Organic Sunflower Oil", "Organic Oils", 260.00, 55, "litre", True, "Karnataka Organic Farms"),
#     ("Organic Safflower Oil", "Organic Oils", 340.00, 35, "litre", True, "Maharashtra Farms"),
#     ("Cold-Pressed Flaxseed Oil", "Organic Oils", 650.00, 30, "litre", True, "Himalayan Organic Farms"),
#     ("Cold-Pressed Avocado Oil", "Organic Oils", 850.00, 25, "litre", True, "Organic Valley Farms"),
#     ("Organic Olive Oil", "Organic Oils", 750.00, 40, "litre", True, "Indian Organic Oils"),
#     ("Extra Virgin Olive Oil", "Organic Oils", 900.00, 30, "litre", True, "Indian Organic Oils"),
#     ("Organic Rice Bran Oil", "Organic Oils", 290.00, 50, "litre", True, "Demo Organic Farms"),
#     ("Cold-Pressed Walnut Oil", "Organic Oils", 780.00, 20, "litre", True, "Himachal Organic Farms"),
#     ("Cold-Pressed Almond Oil", "Organic Oils", 950.00, 25, "litre", True, "Rajasthan Organic Farms"),
#     ("Organic Sesame Cooking Oil", "Organic Oils", 380.00, 45, "litre", True, "Tamil Nadu Organic Farms"),
#     ("Virgin Coconut Oil", "Organic Oils", 420.00, 40, "litre", True, "Kerala Organic Oils"),
#     ("Organic Hemp Seed Oil", "Organic Oils", 1100.00, 15, "litre", True, "Organic Valley Farms"),
#     ("Cold-Pressed Castor Oil", "Organic Oils", 260.00, 35, "litre", True, "Rajasthan Organic Farms"),
#     ("Organic Moringa Oil", "Organic Oils", 900.00, 20, "litre", True, "Tamil Nadu Organic Farms"),
#     ("Cold-Pressed Neem Oil", "Organic Oils", 350.00, 30, "litre", True, "Karnataka Organic Farms"),
#     ("Organic Mustard Seed Oil", "Organic Oils", 310.00, 45, "litre", True, "Rajasthan Organic Farms"),

#     # ========================================================================
#     # JUICES & BEVERAGES - 20
#     # ========================================================================

#     ("Fresh Sugarcane Juice Concentrate", "Juices & Beverages", 150.00, 30, "litre", False, None),
#     ("Organic Amla Juice", "Juices & Beverages", 180.00, 35, "litre", True, "Demo Organic Farms"),
#     ("Organic Mango Juice", "Juices & Beverages", 220.00, 40, "litre", True, "Konkan Organic Farms"),
#     ("Organic Orange Juice", "Juices & Beverages", 190.00, 45, "litre", True, "Nagpur Organic Farms"),
#     ("Organic Apple Juice", "Juices & Beverages", 240.00, 35, "litre", True, "Himachal Organic Farms"),
#     ("Organic Pomegranate Juice", "Juices & Beverages", 280.00, 30, "litre", True, "Demo Organic Farms"),
#     ("Organic Pineapple Juice", "Juices & Beverages", 210.00, 40, "litre", True, "Kerala Organic Farms"),
#     ("Organic Guava Juice", "Juices & Beverages", 180.00, 35, "litre", True, "Demo Organic Farms"),
#     ("Tender Coconut Water", "Juices & Beverages", 120.00, 60, "litre", True, "Kerala Organic Farms"),
#     ("Organic Lemon Ginger Drink", "Juices & Beverages", 160.00, 50, "litre", True, "Demo Organic Farms"),
#     ("Organic Beetroot Juice", "Juices & Beverages", 200.00, 35, "litre", True, "Karnataka Organic Farms"),
#     ("Organic Carrot Juice", "Juices & Beverages", 190.00, 40, "litre", True, "Demo Organic Farms"),
#     ("Organic Mixed Fruit Juice", "Juices & Beverages", 230.00, 45, "litre", True, "Demo Organic Farms"),
#     ("Organic Kokum Juice", "Juices & Beverages", 220.00, 30, "litre", True, "Konkan Organic Farms"),
#     ("Organic Jamun Juice", "Juices & Beverages", 250.00, 25, "litre", True, "Karnataka Organic Farms"),
#     ("Organic Wheatgrass Juice", "Juices & Beverages", 320.00, 20, "litre", True, "Demo Organic Farms"),
#     ("Organic Tulsi Herbal Drink", "Juices & Beverages", 180.00, 40, "litre", True, "Demo Organic Farms"),
#     ("Organic Cucumber Mint Juice", "Juices & Beverages", 170.00, 35, "litre", True, "Karnataka Organic Farms"),
#     ("Organic Aloe Vera Drink", "Juices & Beverages", 200.00, 30, "litre", True, "Demo Organic Farms"),
#     ("Organic Ginger Lemonade", "Juices & Beverages", 150.00, 50, "litre", True, "Demo Organic Farms"),

#     # ========================================================================
#     # GRAINS & PULSES - 25
#     # ========================================================================

#     ("Organic Brown Rice", "Grains & Pulses", 95.00, 200, "kg", True, "Demo Organic Farms"),
#     ("Organic Toor Dal", "Grains & Pulses", 140.00, 150, "kg", True, "Demo Organic Farms"),
#     ("Organic Basmati Rice", "Grains & Pulses", 180.00, 120, "kg", True, "Punjab Organic Farms"),
#     ("Organic Sona Masoori Rice", "Grains & Pulses", 110.00, 180, "kg", True, "Karnataka Organic Farms"),
#     ("Organic Red Rice", "Grains & Pulses", 130.00, 100, "kg", True, "Kerala Organic Farms"),
#     ("Organic Black Rice", "Grains & Pulses", 220.00, 70, "kg", True, "Northeast Organic Farms"),
#     ("Organic Quinoa", "Grains & Pulses", 360.00, 60, "kg", True, "Organic Valley Farms"),
#     ("Organic Foxtail Millet", "Grains & Pulses", 140.00, 90, "kg", True, "Karnataka Organic Farms"),
#     ("Organic Finger Millet", "Grains & Pulses", 100.00, 120, "kg", True, "Karnataka Organic Farms"),
#     ("Organic Pearl Millet", "Grains & Pulses", 95.00, 100, "kg", True, "Rajasthan Organic Farms"),
#     ("Organic Little Millet", "Grains & Pulses", 150.00, 70, "kg", True, "Karnataka Organic Farms"),
#     ("Organic Kodo Millet", "Grains & Pulses", 145.00, 65, "kg", True, "Madhya Pradesh Farms"),
#     ("Organic Barnyard Millet", "Grains & Pulses", 160.00, 60, "kg", True, "Karnataka Organic Farms"),
#     ("Organic Green Moong Dal", "Grains & Pulses", 150.00, 120, "kg", True, "Demo Organic Farms"),
#     ("Organic Black Urad Dal", "Grains & Pulses", 170.00, 100, "kg", True, "Demo Organic Farms"),
#     ("Organic Chana Dal", "Grains & Pulses", 125.00, 140, "kg", True, "Rajasthan Organic Farms"),
#     ("Organic Masoor Dal", "Grains & Pulses", 135.00, 130, "kg", True, "Madhya Pradesh Farms"),
#     ("Organic Kabuli Chana", "Grains & Pulses", 160.00, 100, "kg", True, "Rajasthan Organic Farms"),
#     ("Organic Rajma", "Grains & Pulses", 190.00, 90, "kg", True, "Himachal Organic Farms"),
#     ("Organic Black Chana", "Grains & Pulses", 120.00, 110, "kg", True, "Rajasthan Organic Farms"),
#     ("Organic Green Gram", "Grains & Pulses", 145.00, 100, "kg", True, "Karnataka Organic Farms"),
#     ("Organic Red Kidney Beans", "Grains & Pulses", 180.00, 80, "kg", True, "Himachal Organic Farms"),
#     ("Organic Barley", "Grains & Pulses", 90.00, 100, "kg", True, "Punjab Organic Farms"),
#     ("Organic Rolled Oats", "Grains & Pulses", 180.00, 90, "kg", True, "Organic Valley Farms"),
#     ("Organic Broken Wheat", "Grains & Pulses", 85.00, 120, "kg", True, "Punjab Organic Farms"),

#     # ========================================================================
#     # SPICES - 25
#     # ========================================================================

#     ("Organic Turmeric Powder", "Spices", 90.00, 80, "kg", True, "Demo Organic Farms"),
#     ("Organic Black Pepper", "Spices", 480.00, 25, "kg", True, "Kerala Organic Oils"),
#     ("Organic Cumin Seeds", "Spices", 360.00, 40, "kg", True, "Rajasthan Organic Farms"),
#     ("Organic Coriander Powder", "Spices", 180.00, 55, "kg", True, "Rajasthan Organic Farms"),
#     ("Organic Red Chilli Powder", "Spices", 220.00, 50, "kg", True, "Andhra Organic Farms"),
#     ("Organic Green Cardamom", "Spices", 1800.00, 15, "kg", True, "Kerala Organic Farms"),
#     ("Organic Cloves", "Spices", 1100.00, 20, "kg", True, "Kerala Organic Farms"),
#     ("Organic Cinnamon", "Spices", 700.00, 25, "kg", True, "Kerala Organic Farms"),
#     ("Organic Fennel Seeds", "Spices", 250.00, 35, "kg", True, "Rajasthan Organic Farms"),
#     ("Organic Fenugreek Seeds", "Spices", 180.00, 40, "kg", True, "Rajasthan Organic Farms"),
#     ("Organic Mustard Seeds", "Spices", 140.00, 45, "kg", True, "Rajasthan Organic Farms"),
#     ("Organic Ajwain", "Spices", 300.00, 30, "kg", True, "Rajasthan Organic Farms"),
#     ("Organic Bay Leaves", "Spices", 450.00, 20, "kg", True, "Kerala Organic Farms"),
#     ("Organic Star Anise", "Spices", 900.00, 15, "kg", True, "Northeast Organic Farms"),
#     ("Organic Nutmeg", "Spices", 1000.00, 18, "kg", True, "Kerala Organic Farms"),
#     ("Organic Mace", "Spices", 1500.00, 12, "kg", True, "Kerala Organic Farms"),
#     ("Organic Dry Ginger", "Spices", 380.00, 25, "kg", True, "Kerala Organic Farms"),
#     ("Organic Asafoetida", "Spices", 1200.00, 15, "kg", True, "Demo Organic Farms"),
#     ("Organic Garam Masala", "Spices", 300.00, 40, "kg", True, "Demo Organic Farms"),
#     ("Organic Sambar Powder", "Spices", 280.00, 45, "kg", True, "Karnataka Organic Farms"),
#     ("Organic Rasam Powder", "Spices", 290.00, 40, "kg", True, "Karnataka Organic Farms"),
#     ("Organic Curry Powder", "Spices", 320.00, 35, "kg", True, "Kerala Organic Farms"),
#     ("Organic Chaat Masala", "Spices", 280.00, 30, "kg", True, "Rajasthan Organic Farms"),
#     ("Organic Kashmiri Chilli Powder", "Spices", 400.00, 25, "kg", True, "Kashmir Organic Farms"),
#     ("Organic Panch Phoron", "Spices", 250.00, 30, "kg", True, "West Bengal Organic Farms"),

#     # ========================================================================
#     # SNACKS - 25
#     # ========================================================================

#     ("Roasted Makhana (Fox Nuts)", "Snacks", 260.00, 60, "kg", False, None),
#     ("Mixed Dry Fruit Trail Mix", "Snacks", 350.00, 40, "kg", False, None),
#     ("Organic Almonds", "Snacks", 850.00, 50, "kg", True, "Kashmir Organic Farms"),
#     ("Organic Cashews", "Snacks", 900.00, 45, "kg", True, "Goa Organic Farms"),
#     ("Organic Walnuts", "Snacks", 950.00, 35, "kg", True, "Kashmir Organic Farms"),
#     ("Organic Raisins", "Snacks", 420.00, 55, "kg", True, "Maharashtra Farms"),
#     ("Organic Dates", "Snacks", 500.00, 60, "kg", True, "Organic Valley Farms"),
#     ("Organic Pistachios", "Snacks", 1100.00, 30, "kg", True, "Organic Valley Farms"),
#     ("Roasted Chickpeas", "Snacks", 220.00, 70, "kg", True, "Rajasthan Organic Farms"),
#     ("Organic Peanut Chikki", "Snacks", 280.00, 60, "kg", True, "Karnataka Organic Farms"),
#     ("Organic Sesame Chikki", "Snacks", 300.00, 50, "kg", True, "Karnataka Organic Farms"),
#     ("Organic Jowar Puffs", "Snacks", 180.00, 65, "kg", True, "Maharashtra Farms"),
#     ("Organic Ragi Chips", "Snacks", 220.00, 60, "kg", True, "Karnataka Organic Farms"),
#     ("Organic Banana Chips", "Snacks", 240.00, 70, "kg", True, "Kerala Organic Farms"),
#     ("Organic Jackfruit Chips", "Snacks", 280.00, 50, "kg", True, "Kerala Organic Farms"),
#     ("Organic Sweet Potato Chips", "Snacks", 260.00, 45, "kg", True, "Karnataka Organic Farms"),
#     ("Organic Millet Cookies", "Snacks", 320.00, 50, "kg", True, "Demo Organic Farms"),
#     ("Organic Oat Cookies", "Snacks", 300.00, 55, "kg", True, "Demo Organic Farms"),
#     ("Organic Coconut Cookies", "Snacks", 340.00, 40, "kg", True, "Kerala Organic Farms"),
#     ("Organic Granola", "Snacks", 450.00, 35, "kg", True, "Organic Valley Farms"),
#     ("Organic Trail Mix", "Snacks", 500.00, 40, "kg", True, "Organic Valley Farms"),
#     ("Roasted Pumpkin Seeds", "Snacks", 650.00, 30, "kg", True, "Organic Valley Farms"),
#     ("Roasted Sunflower Seeds", "Snacks", 450.00, 35, "kg", True, "Organic Valley Farms"),
#     ("Organic Coconut Chips", "Snacks", 380.00, 40, "kg", True, "Kerala Organic Farms"),
#     ("Organic Murukku", "Snacks", 320.00, 45, "kg", True, "Karnataka Organic Farms"),

#     # ========================================================================
#     # HONEY & SWEETENERS - 15
#     # ========================================================================

#     ("Raw Forest Honey", "Honey & Sweeteners", 420.00, 55, "kg", True, "Demo Organic Farms"),
#     ("Organic Jaggery", "Honey & Sweeteners", 85.00, 100, "kg", True, "Demo Organic Farms"),
#     ("Organic Jaggery Powder", "Honey & Sweeteners", 110.00, 90, "kg", True, "Karnataka Organic Farms"),
#     ("Raw Multifloral Honey", "Honey & Sweeteners", 450.00, 50, "kg", True, "Demo Organic Farms"),
#     ("Organic Wildflower Honey", "Honey & Sweeteners", 480.00, 45, "kg", True, "Himalayan Organic Farms"),
#     ("Organic Acacia Honey", "Honey & Sweeteners", 550.00, 35, "kg", True, "Organic Valley Farms"),
#     ("Organic Neem Honey", "Honey & Sweeteners", 500.00, 30, "kg", True, "Karnataka Organic Farms"),
#     ("Organic Jamun Honey", "Honey & Sweeteners", 520.00, 30, "kg", True, "Karnataka Organic Farms"),
#     ("Organic Date Syrup", "Honey & Sweeteners", 450.00, 35, "litre", True, "Organic Valley Farms"),
#     ("Organic Coconut Sugar", "Honey & Sweeteners", 380.00, 40, "kg", True, "Kerala Organic Farms"),
#     ("Organic Palm Jaggery", "Honey & Sweeteners", 180.00, 60, "kg", True, "Tamil Nadu Organic Farms"),
#     ("Organic Cane Sugar", "Honey & Sweeteners", 120.00, 80, "kg", True, "Karnataka Organic Farms"),
#     ("Organic Stevia Powder", "Honey & Sweeteners", 650.00, 25, "kg", True, "Organic Valley Farms"),
#     ("Organic Maple Syrup", "Honey & Sweeteners", 900.00, 25, "litre", True, "Organic Valley Farms"),
#     ("Organic Agave Syrup", "Honey & Sweeteners", 700.00, 25, "litre", True, "Organic Valley Farms"),

#     # ========================================================================
#     # PERSONAL CARE - 15
#     # ========================================================================

#     ("Organic Aloe Vera Gel", "Personal Care", 199.00, 70, "piece", True, "Demo Organic Farms"),
#     ("Herbal Neem Soap", "Personal Care", 60.00, 150, "piece", False, None),
#     ("Organic Turmeric Soap", "Personal Care", 75.00, 100, "piece", True, "Demo Organic Farms"),
#     ("Organic Sandalwood Soap", "Personal Care", 110.00, 80, "piece", True, "Karnataka Organic Farms"),
#     ("Organic Coconut Soap", "Personal Care", 80.00, 90, "piece", True, "Kerala Organic Farms"),
#     ("Organic Rose Face Wash", "Personal Care", 220.00, 60, "piece", True, "Demo Organic Farms"),
#     ("Organic Neem Face Wash", "Personal Care", 210.00, 65, "piece", True, "Demo Organic Farms"),
#     ("Organic Aloe Face Wash", "Personal Care", 230.00, 60, "piece", True, "Demo Organic Farms"),
#     ("Organic Coconut Shampoo", "Personal Care", 280.00, 55, "piece", True, "Kerala Organic Farms"),
#     ("Organic Hibiscus Shampoo", "Personal Care", 300.00, 50, "piece", True, "Karnataka Organic Farms"),
#     ("Organic Amla Hair Oil", "Personal Care", 260.00, 60, "piece", True, "Demo Organic Farms"),
#     ("Organic Coconut Hair Oil", "Personal Care", 240.00, 70, "piece", True, "Kerala Organic Farms"),
#     ("Organic Rose Water", "Personal Care", 180.00, 75, "piece", True, "Rajasthan Organic Farms"),
#     ("Organic Neem Powder", "Personal Care", 160.00, 50, "kg", True, "Karnataka Organic Farms"),
#     ("Organic Multani Mitti", "Personal Care", 140.00, 60, "kg", True, "Rajasthan Organic Farms"),
# ]


# # ============================================================================
# # DEMO / SEED PRODUCT IMAGES
# #
# # Seed images are optional. Products without a verified seed image use None.
# # Duplicate image URLs from the previous mapping were removed.
# # Vendor-uploaded images can replace these values later.
# # ============================================================================

# PRODUCT_IMAGES = {
#     'Alphonso Mangoes': 'https://images.unsplash.com/photo-1553279768-865429fa0078?auto=format&fit=crop&w=900&q=85',
#     'Organic Bananas': 'https://images.unsplash.com/photo-1571771894821-ce9b6c11b08e?auto=format&fit=crop&w=900&q=85',
#     'Fuji Apples': 'https://www.saudifruit.sa/images/products-new/Fuji-Apples.jpg',
#     'Kashmiri Apples': 'https://cf-img-a-in.tosshub.com/sites/visualstory/wp/2025/04/Kashmiri-ApplesITG-1745658119536.webp?size=%2A%3A900',
#     'Kesar Mangoes': 'https://www.mangodatabase.com/images/varieties/whc65b65037d718f_f5QYmDjJYY_S212HU5oUr.jpg',
#     'Organic Papaya': 'https://images.unsplash.com/photo-1556719240-31629484142a?auto=format&fit=crop&w=900&q=85',
#     'Fresh Pineapple': 'https://upload.wikimedia.org/wikipedia/commons/9/9c/Fresh_Pineapple_Fruits.jpg',
#     'Organic Watermelon': 'https://upload.wikimedia.org/wikipedia/commons/b/b9/Watermelon.jpg',
#     'Green Grapes': 'https://cdn.salla.sa/apBzl/l18qeaR39amloRUWuQKfkNuBxmU79xYxhpSrWOlP.jpg',
#     'Black Grapes': 'https://upload.wikimedia.org/wikipedia/commons/a/a7/Black_grapes_in_a_bowl.jpg',
#     'Organic Pomegranate': 'https://tiimg.tistatic.com/fp/1/008/340/sweet-delicious-taste-natural-round-organic-pomegranate-299.jpg',
#     'Sweet Lime': 'https://commons.wikimedia.org/wiki/Special:Redirect/file/%22Sweet_lime_of_Salem%22.jpg',
#     'Organic Oranges': 'https://sgwetmarket.com.sg/cdn/shop/products/2.orange-navel-313149.jpg?v=1593132715',
#     'Mosambi': 'https://commons.wikimedia.org/wiki/Special:Redirect/file/(Citrus%20limetta)%20Mosambi%20at%20a%20market%20in%20Seethammadhara.jpg',
#     'Organic Guava': 'https://www.agroexporters.net/uploaded-files/thumb-cache/member_127/thumb---guava_4999.jpg',
#     'Dragon Fruit': 'https://img.clevup.in/278008/SKU-0195_0-1720803662130.jpg?format=webp&width=600',
#     'Organic Kiwi': 'https://images.unsplash.com/photo-1539461007403-49f413d10b64?auto=format&fit=crop&w=900&q=85',
#     'Fresh Strawberries': 'https://www.ars.usda.gov/ARSUserFiles/oc/images/photos/featuredphoto/aug23/D3073-1w.jpg',
#     'Organic Pears': 'https://d2j6dbq0eux0bg.cloudfront.net/images/7152101/2379575823.jpg',
#     'Custard Apple': 'https://pluckk.s3.ap-south-1.amazonaws.com/uploads/3153-untitled-design-61.jpg',
#     'Organic Sapota': 'https://static.wixstatic.com/media/1536ae_98951bff631244c58fd8971e2857a88e~mv2.jpg/v1/fit/w_500%2Ch_500%2Cq_90/file.jpg',
#     'Fresh Coconut': 'https://www.metro-online.pk/_next/image?q=75&url=https%3A%2F%2Fprodimages.metro-online.pk%2FProducts%2F1689767373521.jpg&w=3840',
#     'Tender Coconut': 'https://commons.wikimedia.org/wiki/Special:Redirect/file/Tender_coconut.jpg',
#     'Organic Plums': 'https://i1.pickpik.com/photos/126/714/474/plum-fruit-fruits-violet-purple-preview.jpg',
#     'Fresh Chikoo': 'https://services.kpnfresh.com/media/v1/products/images/09e3b8d5-2f6e-4194-955b-3f723479718e/chikoo.webp?c_type=C2',
#     'Organic Spinach': 'https://images.unsplash.com/photo-1576045057995-568f588f82fb?auto=format&fit=crop&w=900&q=85',
#     'Heirloom Tomatoes': 'https://images.unsplash.com/photo-1546094096-0df4bcaaa337?auto=format&fit=crop&w=900&q=85',
#     'Organic Carrots': 'https://images.unsplash.com/photo-1445282768818-728615cc910a?auto=format&fit=crop&w=900&q=85',
#     'Organic Potatoes': 'https://images.unsplash.com/photo-1508313880080-c4bef0730395?auto=format&fit=crop&w=900&q=85',
#     'Organic Onions': 'https://www.publicdomainpictures.net/en/view-image.php?image=8303&large=1&picture=organic-onions',
#     'Green Capsicum': 'http://www.public-domain-image.com/full-image/flora-plants-public-domain-images-pictures/vegetables-public-domain-images-pictures/pepper-pictures/green-capsicum.jpg',
#     'Red Capsicum': 'https://paddocktopantry.co.nz/cdn/shop/products/redcapsicum_900x.jpg?v=1693345796',
#     'Yellow Capsicum': 'https://fruitworld.co.nz/cdn/shop/products/yellow_capsicum_pepper.png?v=1606363843&width=1000',
#     'Organic Cucumber': 'https://images.unsplash.com/photo-1523349462262-054f5b3aa500?auto=format&fit=crop&w=900&q=85',
#     'Organic Beetroot': 'https://organicbazar.net/cdn/shop/products/Beetroot-Seeds-2.jpg?v=1694167537',
#     'Fresh Broccoli': 'https://images.unsplash.com/photo-1518164147695-36c13dd568f5?auto=format&fit=crop&w=900&q=85',
#     'Organic Cauliflower': 'https://images.unsplash.com/photo-1558108722-d672acd746b8?auto=format&fit=crop&w=900&q=85',
#     'Organic Cabbage': 'https://superbhyper.co.za/wp-content/uploads/2023/06/CABBAGE.jpg',
#     'Green Beans': 'https://www.podtatranskadebnicka.sk/application/layouts/product-images/100/100-202.jpg',
#     'French Beans': 'https://dukaan.b-cdn.net/500x500/webp/4075118/f9265ecb-b431-4f32-8deb-435b516c6d0c/french-beans1-56bfad07-42eb-4e15-9d2e-acf00f34ce8a.jpg',
#     'Organic Green Peas': 'https://www.kibsons.com/_next/image?q=90&url=https%3A%2F%2Fcdn.kibsons.com%2Fproducts%2Fdetail%2FHPL_PEAGRPKXX04KA1_20251208115708.jpg&w=640',
#     'Lady Finger': 'https://msosi.jumlajumla.com/_next/image?q=75&url=https%3A%2F%2Fmsosijumla.s3.eu-north-1.amazonaws.com%2Fpublic%2Fimages%2Fproducts%2F122-17459167781772.webp&w=3840',
#     'Organic Brinjal': 'https://images.unsplash.com/photo-1647134619933-452c43b63970?auto=format&fit=crop&w=900&q=85',
#     'Bottle Gourd': 'https://commons.wikimedia.org/wiki/Special:Redirect/file/Bottle%20Gourd.jpg',
#     'Ridge Gourd': 'https://commons.wikimedia.org/wiki/Special:Redirect/file/Ridge%20Gourd.jpg',
#     'Bitter Gourd': 'https://eshop.supernature.com.sg/cdn/shop/files/Bitter_gourd_1200x1200.jpg?v=1747106645',
#     'Drumstick': 'https://toronto.motherlandgrocery.ca/cdn/shop/products/11503.png?v=1614908550',
#     'Sweet Corn': 'https://www.bastanastore.com/cdn/shop/products/sweetcorn.jpg?v=1611047027',
#     'Organic Pumpkin': 'https://cdn.hstatic.net/products/200000692807/bi_do_4dc1a183575040499832240426b1dc5e_master.png',
#     'Radish': 'https://images.mathem.se/prod/local_products/c81f09a7-4323-4961-975f-485427b6bff8.jpg?fit=bounds&format=auto&optimize=medium&s=0xef25f48d3a4da6a2d3d1b1de87eaa5a69b099084&width=1000',
#     'Turnip': 'https://commons.wikimedia.org/wiki/Special:Redirect/file/Turnips.jpg',
#     'Organic Fenugreek Leaves': 'https://image.cdn.shpy.in/372001/SKU-0339_2-1730532147044.jpg?format=webp',
#     'Coriander Leaves': 'https://joualvert.ca/cdn/shop/products/coriander_bb8d7913-fd8b-432e-a7b3-9e8561dbc823.jpg?v=1698701297',
#     'Curry Leaves': 'https://www.asiatischer-lebensmittelladen.de/wp-content/uploads/2024/02/fresh-curry-leaves-isolated-on-600nw-1383411830.jpg.jpg',
#     'Organic Garlic': 'https://untamedearth.nz/cdn/shop/products/WhatsAppImage2022-12-01at2.57.29PM_grande.jpg?v=1669860631',
#     'Cold-Pressed Coconut Oil': 'https://www.bbassets.com/media/uploads/p/l/40359966_1-saffola-cold-pressed-coconut-oil.jpg',
#     'Cold-Pressed Groundnut Oil': 'https://organicindia.com/cdn/shop/files/GroundnutOil1LtrBottle.png?v=1765865678&width=416',
#     'Cold-Pressed Sesame Oil': 'https://excellafoods.com/cdn/shop/files/coldpresssesameoilcanvaedit.png?v=1738312913&width=500',
#     'Cold-Pressed Mustard Oil': 'https://www.jiomart.com/images/product/original/494626147/saffola-cold-pressed-mustard-oil-1-l-product-images-o494626147-p612062510-0-202507301829.jpg?im=Resize%3D%281000%2C1000%29',
#     'Organic Sunflower Oil': 'https://static.ah.nl/dam/product/AHI_434d50313036313232?fileType=binary&rendition=800x800_JPG_Q90&revLabel=3',
#     'Organic Safflower Oil': 'https://lamoisson.com/cdn/shop/files/natur-huile-de-carthame-450ml.jpg?v=1752863776',
#     'Cold-Pressed Flaxseed Oil': 'https://sunshinemarket.co.th/cdn/shop/files/Untitled-1-1.png?v=1722836486',
#     'Cold-Pressed Avocado Oil': 'https://cdn.mafrservices.com/sys-master-root/ha9/hd1/35171081289758/1657615_main.jpg',
#     'Organic Olive Oil': 'https://media-stark.gourmetmarketthailand.com/products/thumbnail/8859414000395-1.webp',
#     'Extra Virgin Olive Oil': None,
#     'Organic Rice Bran Oil': 'https://sg-live-01.slatic.net/p/f223a03b20da421a05fed6e7259a571a.jpg',
#     'Cold-Pressed Walnut Oil': 'https://www.bestofhungary.co.uk/cdn/shop/files/OrganicWalnutOil250ml.jpg?v=1697444585&width=1214',
#     'Cold-Pressed Almond Oil': 'https://www.niharti.com/image/cache/catalog/almond-oil-1l-700x700.jpg',
#     'Organic Sesame Cooking Oil': 'https://commons.wikimedia.org/wiki/Special:Redirect/file/Sesame_oil.jpg',
#     'Virgin Coconut Oil': 'https://www.sutrakart.com/cdn/shop/files/Pure_Cold_Pressed_Virgin_Coconut_Oil.png?v=1775559484',
#     'Organic Hemp Seed Oil': 'https://www.gagneensante.com/cdn/shop/products/huile-de-chanvre-biologique-624004.png?v=1762533776',
#     'Cold-Pressed Castor Oil': 'https://d2j6dbq0eux0bg.cloudfront.net/images/63607701/products/624408487/5522357313.jpg',
#     'Organic Moringa Oil': 'https://i5.walmartimages.com/seo/Plantlife-Moringa-Carrier-Oil-Cold-Pressed-Non-GMO-and-Gluten-Free-Carrier-Oils-For-Skin-Hair-and-Personal-Care-2-oz_eeed09fe-f279-44db-9bd8-c22382d8e897.1b97cadf537b5d072e088be8a35408da.jpeg',
#     'Cold-Pressed Neem Oil': 'https://puroestadofisico.com/cdn/shop/files/Best-Naturals-Aceite-De-Neem-473ml_800x.jpg?v=1710888139',
#     'Organic Mustard Seed Oil': None,
#     'Fresh Sugarcane Juice Concentrate': 'https://images.unsplash.com/photo-1622597467836-f3285f2131b8?auto=format&fit=crop&w=900&q=85',
#     'Organic Amla Juice': 'https://commons.wikimedia.org/wiki/Special:Redirect/file/Amla_juice.jpg',
#     'Organic Mango Juice': 'https://matjrah.online/images/1404/image/cache/catalog/1692707173-8-1100x1100.jpg',
#     'Organic Orange Juice': None,
#     'Organic Apple Juice': 'https://dg6qn11ynnp6a.cloudfront.net/wp-content/uploads/2023/04/04105423/632856345.martinelli.s.1l.organic-scaled.jpg',
#     'Organic Pomegranate Juice': 'https://damassupermarket.com/2269-large_default/red-crown-organic-pomegranate-juice-1l-.jpg',
#     'Organic Pineapple Juice': 'https://orderacme.s3.amazonaws.com/ProductImages/00074682107340.full.jpg',
#     'Organic Guava Juice': None,
#     'Tender Coconut Water': 'https://www.pinoygrocers.com/cdn/shop/files/ee9a6f9f-1668-488e-9fd9-fe1eb6ecfe97_8906009300566_018af5f8-f51a-42d6-a15c-c4c4a49f9251.webp?v=1765823119',
#     'Organic Lemon Ginger Drink': None,
#     'Organic Beetroot Juice': 'https://www.realfoods.co.uk/ProductImagesID/3389_1.jpg',
#     'Organic Carrot Juice': 'https://cdn.salla.sa/RAxnwP/f0885e4c-bc6f-4492-9b4e-82f684698178-1000x1000-IuaL2pz135fOUnkRTrb3BnCVoKjnnie30ISxi4KL.png',
#     'Organic Mixed Fruit Juice': None,
#     'Organic Kokum Juice': None,
#     'Organic Jamun Juice': 'https://freshmills.in/cdn/shop/files/organic-jamun-juice-867719.jpg?v=1717362174&width=1500',
#     'Organic Wheatgrass Juice': 'https://vinut.com.vn/wp-content/webp-express/webp-images/uploads/2019/12/300ml_Bottled_WheatGrass_Juice_Drink_Original-600x600.jpg.webp',
#     'Organic Tulsi Herbal Drink': None,
#     'Organic Cucumber Mint Juice': 'https://i.ebayimg.com/images/g/5PIAAOSwdsVmbP0R/s-l1200.jpg',
#     'Organic Aloe Vera Drink': 'https://cdnprod.mafretailproxy.com/sys-master-root/h23/ha1/26758313803806/748853_main.jpg_480Wx480H',
#     'Organic Ginger Lemonade': None,
#     'Organic Brown Rice': 'https://i5.walmartimages.com/asr/b17e9da2-9904-49f2-882b-f3debd34e657_1.224a11ad9cef553c3124da53a21c821d.jpeg?odnBg=ffffff&odnHeight=1000&odnWidth=1000',
#     'Organic Toor Dal': 'https://i5.walmartimages.com/seo/Sheel-Organic-Toor-Dal-Split-Pigeon-Pea-4-lbs_59d26111-dd40-44e1-bb08-aefcf7d8c87a.da1f04f304491caa1fe128aa35ca0895.jpeg?odnBg=FFFFFF&odnHeight=768&odnWidth=768',
#     'Organic Basmati Rice': 'https://img3.21food.com/img/product/2020/11/19/food3052421605749450953875.jpg',
#     'Organic Sona Masoori Rice': 'https://www.thefastrack.co.uk/uploads/products/view/1745176259.jpg',
#     'Organic Red Rice': 'https://www.ecohoy.com/media/catalog/product/cache/1/thumbnail/600x/9df78eab33525d08d6e5fb8d27136e95/O/r/OrganicsRedRice1Kg1800x1000.jpg',
#     'Organic Black Rice': 'https://i.ebayimg.com/images/g/6fsAAOSw3ZVjVWpJ/s-l1200.jpg',
#     'Organic Quinoa': 'https://etara-online.com/photos/shares/2022/test/20/G08-quinoa-grain-main.jpg',
#     'Organic Foxtail Millet': 'https://www.smartfood.org/wp-content/uploads/2020/10/foxtail-husk-off-1-930x1024.png',
#     'Organic Finger Millet': 'https://img.etimg.com/thumb/msid-128813492%2Cwidth-640%2Cheight-480%2Cimgsize-84604%2Cresizemode-4/finger-millet-ragi-the-iron-dense-grain.jpg',
#     'Organic Pearl Millet': 'https://media.post.rvohealth.io/wp-content/uploads/2020/10/bajra-pearl-millet-grain-732x549-thumbnail-732x549.jpg',
#     'Organic Little Millet': 'https://bazaar5.com/image/cache/catalog/pro/product/apiData/b00pagno98-24-mantra-little-millet-500gms-pack-of-1-100-organic-chemical-free-pesticides-free-gluten-free--0-2000x2000.jpg',
#     'Organic Kodo Millet': 'https://cdn.shopify.com/s/files/1/2598/1404/files/Buykodomilletonline-img.webp',
#     'Organic Barnyard Millet': 'https://cpimg.tistatic.com/10951881/b/4/barnyard-millet.jpg',
#     'Organic Green Moong Dal': 'https://tiimg.tistatic.com/fp/1/007/562/100-percent-fresh-natural-chemical-pesticide-free-unpolished-green-moong-daal--635.jpg',
#     'Organic Black Urad Dal': 'https://www.jiomart.com/images/product/600x600/rv7w6fhi8z/soni-farms-organic-unpolished-kali-urad-dal-sabut-urad-black-whole-2-kg-product-images-orv7w6fhi8z-p593790207-0-202209152122.jpg',
#     'Organic Chana Dal': 'https://www.jiomart.com/images/product/original/490024261/rajdhani-chana-dal-2-kg-product-images-o490024261-p590882244-0-202506201725.jpg?im=Resize%3D%281000%2C1000%29',
#     'Organic Masoor Dal': 'https://www.starquik.com/cdn/shop/files/SQ111809_FOP_910ec918-3d59-497e-8ed3-733314a5080a.jpg?v=1775027193&width=533',
#     'Organic Kabuli Chana': 'https://img06.weeecdn.com/product/image/597/893/40FF56298584F3B4.jpeg',
#     'Organic Rajma': None,
#     'Organic Black Chana': 'https://ikaiorganic.com/cdn/shop/files/Gemini_Generated_Image_r4n8wmr4n8wmr4n8.png?v=1782288840',
#     'Organic Green Gram': 'https://i.ebayimg.com/images/g/hGMAAOSwr1hmblMG/s-l500.jpg',
#     'Organic Red Kidney Beans': 'https://lifegid.com/media/res/1/3/9/2/1/13921.p060y0.600.jpg',
#     'Organic Barley': 'https://wholefoodsbox.co.uk/cdn/shop/files/jn188.jpg?v=1719084630',
#     'Organic Rolled Oats': 'https://vavapantry.com.au/cdn/shop/products/kialla-rolled-oats-organic-australia_1092c8e4-14be-4b97-a84a-7b9f46ec9fb9_1400x.png?v=1593592943',
#     'Organic Broken Wheat': 'https://puretreefoods.com/cdn/shop/files/PT0084-000400BP.MAIN.jpg?v=1750417054',
#     'Organic Turmeric Powder': 'https://images.unsplash.com/photo-1615485500704-8e990f9900f7?auto=format&fit=crop&w=900&q=85',
#     'Organic Black Pepper': None,
#     'Organic Cumin Seeds': 'https://thamesorganic.com/cdn/shop/files/Organic_Cumin_Seeds_100_gr_1200x1200.jpg?v=1768397343',
#     'Organic Coriander Powder': 'https://i5.walmartimages.com/seo/USDA-Organic-Coriander-Powder-4-oz-Spice-Profile-Freshly-Ground-Dhaniya-Cilantro-Molido-Lab-Tested-for-Purity_275315f5-e589-4126-b3e2-bda5f4b81bc1.9950123d7121617ed3db767e9a287d20.jpeg',
#     'Organic Red Chilli Powder': 'https://melionsbrothers.com/cdn/shop/files/61wxx_CyZrL._SL1080_bb5524fa-a337-4489-b794-fa8ba0ad7d22.jpg?v=1745933839&width=3840',
#     'Organic Green Cardamom': 'https://onsullivan.com/cdn/shop/products/76.jpg?v=1571770395',
#     'Organic Cloves': 'https://i5.walmartimages.com/seo/SPICY-ORGANIC-Cloves-Whole-ESF27-100-Pure-USDA-Organic-Non-GMO-Keto-Friendly-Non-Irradiated-Fresh-Clove-Seed-Spice-4-OZ_4d385cbc-3877-47bd-a6c3-81c97ad4cea8.4e65b038b5533e241f3b14a5c53bd167.jpeg',
#     'Organic Cinnamon': 'https://down-my.img.susercontent.com/file/my-11134207-7r992-lv1jysjjq6go47',
#     'Organic Fennel Seeds': 'https://thamesorganic.com/cdn/shop/files/Organic_Fennel_Seeds_250g_1078x1078.jpg?v=1779324290',
#     'Organic Fenugreek Seeds': 'https://www.jiomart.com/images/product/original/rvpmwkxpjv/24-mantra-organic-fenugreek-seeds-methi-dana-menthi-ginja-100gms-pack-of-1-100-organic-chemical-free-pesticides-free-product-images-orvpmwkxpjv-p606766671-0-202312162047.jpg?im=Resize%3D%281000%2C1000%29',
#     'Organic Mustard Seeds': None,
#     'Organic Ajwain': None,
#     'Organic Bay Leaves': 'https://commons.wikimedia.org/wiki/Special:Redirect/file/Bay_leaves.jpg',
#     'Organic Star Anise': 'https://commons.wikimedia.org/wiki/Special:Redirect/file/Star_anise.jpg',
#     'Organic Nutmeg': 'https://cdn.notonthehighstreet.com/fs/c3/24/316f-b54e-484e-bc80-fa3ee5d59fee/original_organic-whole-nutmeg-100g-for-cooking.jpg',
#     'Organic Mace': None,
#     'Organic Dry Ginger': 'https://5.imimg.com/data5/SELLER/Default/2024/2/389940198/WU/MB/KB/66789684/organic-adrak-500x500.jpg',
#     'Organic Asafoetida': 'https://www.lakshmiayurveda.com.au/cdn/shop/files/IMG_8725.jpg?v=1757337280&width=1200',
#     'Organic Garam Masala': 'https://commons.wikimedia.org/wiki/Special:Redirect/file/Garam_Masala.JPG',
#     'Organic Sambar Powder': 'https://www.gosupps.com/media/catalog/product/cache/25/small_image/1500x1650/9df78eab33525d08d6e5fb8d27136e95/8/1/81nM6FnLDUL_2.jpg',
#     'Organic Rasam Powder': 'https://commons.wikimedia.org/wiki/Special:Redirect/file/Rasam_powder_picture.JPG',
#     'Organic Curry Powder': 'https://commons.wikimedia.org/wiki/Special:Redirect/file/Curry_powder.jpg',
#     'Organic Chaat Masala': 'https://commons.wikimedia.org/wiki/Special:Redirect/file/Chaatmasala.jpg',
#     'Organic Kashmiri Chilli Powder': None,
#     'Organic Panch Phoron': 'https://commons.wikimedia.org/wiki/Special:Redirect/file/Panch-phoron.jpg',
#     'Roasted Makhana (Fox Nuts)': 'https://healthymaster.in/cdn/shop/articles/recipe_for_makhana_chaat.jpg?v=1691743824',
#     'Mixed Dry Fruit Trail Mix': 'https://www.silkrute.com/images/detailed/1951/51YteLqU0yL_kvfs-t2.jpg',
#     'Organic Almonds': 'https://cdn11.bigcommerce.com/s-dis4vxtxtc/images/stencil/608x608/products/2016/5582/Organic-Almonds-1kg-Side-NUALM2.1.2__47624.1665528455.jpg?c=2',
#     'Organic Cashews': 'https://m.media-amazon.com/images/I/51sGFb%2BDSML._SL1000_.jpg',
#     'Organic Walnuts': 'https://cdn0.woolworths.media/content/wowproductimages/large/133476_1.jpg',
#     'Organic Raisins': 'https://cdn11.bigcommerce.com/s-dis4vxtxtc/images/stencil/1280x1280/products/4941/9256/Organic-Raisins-200g-Front-DRRAI2.200__98285.1710740212.jpg?c=2%3Fimbypass%3Don',
#     'Organic Dates': 'https://i5.walmartimages.com/seo/Organic-California-Medjool-Dates-8-Ounces-Non-GMO-Whole-Dry-Fancy-Dates-with-Pits_c2510768-88cf-4389-8f89-4aad0967211c.dd7ddf3d21d054d4022668b272f22d94.jpeg?odnBg=FFFFFF&odnHeight=580&odnWidth=580',
#     'Organic Pistachios': 'https://cdn.shopaccino.com/rootzorganics/products/pistachios-5784084079764246_m.jpg?v=569',
#     'Roasted Chickpeas': 'https://commons.wikimedia.org/wiki/Special:Redirect/file/Roasted_chickpeas.jpg',
#     'Organic Peanut Chikki': 'https://snapcalorie-webflow-website.s3.us-east-2.amazonaws.com/media/food_pics_v2/medium/peanut_chikki.jpg',
#     'Organic Sesame Chikki': 'https://images.indianexpress.com/2019/01/til-chikki.jpg',
#     'Organic Jowar Puffs': 'https://thecowboysfarm.com/cdn/shop/files/CLASSIC_JOWAR_PUFF.jpg?v=1761809674&width=1445',
#     'Organic Ragi Chips': None,
#     'Organic Banana Chips': 'https://naturalhealthorganics.com.au/cdn/shop/products/lotus-organic-banana-chips-150g.jpg?v=1617943615',
#     'Organic Jackfruit Chips': 'https://archipelago-store.com/cdn/shop/files/Screenshot_2024-10-11_at_1.04.57_PM.png?v=1733347084',
#     'Organic Sweet Potato Chips': 'https://balevbiomarket.com/storage/26913/conversions/product_main_image_202708-thumb-620x620.webp',
#     'Organic Millet Cookies': 'https://www.bbassets.com/media/uploads/p/l/40301716_1-gudmom-gluten-free-millet-cookies-100-natural-jaggery.jpg',
#     'Organic Oat Cookies': 'https://www.organics.ph/cdn/shop/files/gullon-bio-organic-cookies-oats-250g-snacks-landers-superstore-sr-membership-shopping-979440_1024x.jpg?v=1748520607',
#     'Organic Coconut Cookies': 'https://cdn.naturamarket.ca/catalog/product/cache/3c698a5d7124ca2538b36bdae68c5d8c/e/m/emmys-organics-coconut-vanilla-min.jpg',
#     'Organic Granola': None,
#     'Organic Trail Mix': 'https://assets.woolworths.com.au/images/1005/763844.jpg?impolicy=wowbumxfyzp',
#     'Roasted Pumpkin Seeds': 'https://cupofyum.com/uploads/images/000/195/183/195183-roasted-pumpkin-seeds-perfectly-crispy-e64d628fc56cdddc85b8df745dfe8125.jpg',
#     'Roasted Sunflower Seeds': 'https://www.zifiti.com/images/itemImgOrig/106/106_2357966.jpg',
#     'Organic Coconut Chips': 'https://thamesorganic.com/cdn/shop/files/Coconut_Chips_100g_1024x1024.jpg?v=1768465997',
#     'Organic Murukku': 'https://cdn.dotpe.in/longtail/store-items/6368205/UcYItuTz.webp',
#     'Raw Forest Honey': 'https://www.bbassets.com/media/uploads/p/xl/40129245_9-natures-nectar-select-honey-forest.jpg',
#     'Organic Jaggery': 'https://www.bbassets.com/media/uploads/p/l/279802_8-24-mantra-organic-jaggery.jpg',
#     'Organic Jaggery Powder': 'https://pureandsure.in/cdn/shop/files/Jaggery-Powder-F_1200x1200.jpg?v=1762237438',
#     'Raw Multifloral Honey': 'https://triphal.com/cdn/shop/files/Raw-Honey-by-Triphal---Pure-Best-Quality-Shahad---1.jpg?crop=center&height=800&v=1779103576&width=800',
#     'Organic Wildflower Honey': 'https://www.realfoods.co.uk/ProductImagesID/44009_1.jpg',
#     'Organic Acacia Honey': 'https://commons.wikimedia.org/wiki/Special:Redirect/file/Honey_1.jpg',
#     'Organic Neem Honey': None,
#     'Organic Jamun Honey': 'https://mirchi.com/os/cdn/content/images/jamun%20honey%20shivaa%20organic_medium_0492448.webp',
#     'Organic Date Syrup': 'https://datules.lt/wp-content/uploads/2024/08/Frontal-Verpackung-scaled.jpg',
#     'Organic Coconut Sugar': 'https://d2lnr5mha7bycj.cloudfront.net/product-image/file/large_37ad13c1-8f6f-4091-9196-b04799c35008.png',
#     'Organic Palm Jaggery': 'https://commons.wikimedia.org/wiki/Special:Redirect/file/Organic_palm_jaggery.jpg',
#     'Organic Cane Sugar': 'https://m.media-amazon.com/images/I/51xXYjecAaL._FMwebp__SR600%2C600_.jpg',
#     'Organic Stevia Powder': 'https://www.novanutritions.com/cdn/shop/products/Banner3_83a3bc28-58c4-441d-91e1-32a2665b79b0_600x600.jpg?v=1681757035',
#     'Organic Maple Syrup': 'https://commons.wikimedia.org/wiki/Special:Redirect/file/Maple_syrup.jpg',
#     'Organic Agave Syrup': 'https://commons.wikimedia.org/wiki/Special:Redirect/file/Agave_syrup.jpg',
#     'Organic Aloe Vera Gel': 'https://commons.wikimedia.org/wiki/Special:Redirect/file/Aloe_vera_gel_%2820241107%29.jpg',
#     'Herbal Neem Soap': 'https://cdn11.bigcommerce.com/s-kg2w7z8739/products/28802/images/81167/M-S814__66846.1731699001.386.513.jpg?c=1',
#     'Organic Turmeric Soap': 'https://pareero.com/cdn/shop/files/turmeric-organic-soap.jpg',
#     'Organic Sandalwood Soap': 'https://www.rootsandmuds.com/cdn/shop/files/6298044190526_3.jpg?v=1754680303&width=533',
#     'Organic Coconut Soap': 'https://phutawan.jp/cdn/shop/files/2112200002221-01.jpg?v=1770865824',
#     'Organic Rose Face Wash': 'https://hnmnaturals.com/cdn/shop/files/rose-face-wash-75ml.jpg',
#     'Organic Neem Face Wash': 'https://www.jiomart.com/images/product/original/rvq8ugrsex/khadi-organique-face-care-combo-rose-water-toner-neem-face-wash-pack-of-2-420-ml-product-images-orvq8ugrsex-p594285586-4-202210060813.jpg?im=Resize%3D%28420%2C420%29',
#     'Organic Aloe Face Wash': 'https://organicbeauty.pk/cdn/shop/files/Aloe_Vera_Face_Wash.jpg?v=1748937955',
#     'Organic Coconut Shampoo': 'https://www.beauty.store.bg/dcrimg/277599/bio-shampoan-s-bio-kokosovo-maslo-planeta-organica.jpg',
#     'Organic Hibiscus Shampoo': 'https://aorganicstore.com/cdn/shop/files/hibiscus-shampoo-pack.png?v=1771442260',
#     'Organic Amla Hair Oil': 'https://khadiorganique.com/cdn/shop/files/Amla02_fefb8c66-cd47-41a9-ad0a-e54ecfa489b7.jpg?v=1735208436',
#     'Organic Coconut Hair Oil': None,
#     'Organic Rose Water': 'https://www.suneetalondon.co.uk/cdn/shop/products/rosewater500ml.jpg?v=1648579971&width=1445',
#     'Organic Neem Powder': 'https://hennahubstore.com/cdn/shop/files/10_3_940x.jpg?v=1743674606',
#     'Organic Multani Mitti': 'https://organicmandyatest.myshopify.com/cdn/shop/files/Multani-Mitti-Front-100g.jpg',
# }

# # ============================================================================
# # CATEGORY IMAGES FOR FRONTEND
# # ============================================================================
# # These are intentionally separate from product image_url values.
# # The current Category model shown in this project does not have an image_url
# # column, so this mapping is safe to import/use from the frontend integration
# # layer. If you add Category.image_url later, seed_categories() can persist it.
# CATEGORY_IMAGES = {'Fruits': 'https://images.unsplash.com/photo-1610832958506-aa56368176cf?auto=format&fit=crop&w=1200&q=85', 'Vegetables': 'https://images.unsplash.com/photo-1540420773420-3366772f4999?auto=format&fit=crop&w=1200&q=85', 'Organic Oils': 'https://images.unsplash.com/photo-1474979266404-7eaacbcd87c5?auto=format&fit=crop&w=1200&q=85', 'Juices & Beverages': 'https://images.unsplash.com/photo-1600271886742-f049cd451bba?auto=format&fit=crop&w=1200&q=85', 'Grains & Pulses': 'https://images.unsplash.com/photo-1586201375761-83865001e31c?auto=format&fit=crop&w=1200&q=85', 'Spices': 'https://images.unsplash.com/photo-1596040033229-a9821ebd058d?auto=format&fit=crop&w=1200&q=85', 'Snacks': 'https://images.unsplash.com/photo-1621939514649-280e2aa8ad25?auto=format&fit=crop&w=1200&q=85', 'Honey & Sweeteners': 'https://images.unsplash.com/photo-1587049352846-4a222e784d38?auto=format&fit=crop&w=1200&q=85', 'Personal Care': 'https://images.unsplash.com/photo-1556229010-6c3f2c9ca5f8?auto=format&fit=crop&w=1200&q=85'}

# # ============================================================================
# # GET PRODUCT IMAGE
# # ============================================================================

# def get_category_image(category_name: str) -> str | None:
#     """Return the frontend category image for a category name."""
#     return CATEGORY_IMAGES.get(category_name)


# def get_product_image(product_name: str, category_name: str) -> str | None:
#     """Return the optional seed image for this exact product name."""
#     return PRODUCT_IMAGES.get(product_name)


# # ============================================================================
# # SEED CATEGORIES
# # ============================================================================

# def seed_categories(db):

#     category_map = {}

#     for name, description in CATEGORIES:

#         category = db.scalar(
#             select(Category).where(
#                 Category.name == name
#             )
#         )

#         if category is None:

#             category = Category(
#                 name=name,
#                 description=description,
#                 is_active=True,
#             )

#             db.add(category)

#             db.flush()

#             print(
#                 f"Created category: {name}"
#             )

#         else:

#             category.description = description
#             category.is_active = True

#             print(
#                 f"Category already exists: {name}"
#             )

#         category_map[name] = category

#     return category_map


# # ============================================================================
# # SEED PRODUCTS
# # ============================================================================

# def seed_products(db, category_map):

#     created = 0
#     updated = 0
#     image_count = 0
#     missing_images = []

#     for (
#         name,
#         category_name,
#         price,
#         stock_quantity,
#         unit,
#         organic,
#         vendor,
#     ) in PRODUCTS:

#         # --------------------------------------------------------------------
#         # Validate category
#         # --------------------------------------------------------------------

#         if category_name not in category_map:

#             raise ValueError(
#                 f"Unknown category '{category_name}' "
#                 f"for product '{name}'"
#             )

#         category = category_map[category_name]

#         # --------------------------------------------------------------------
#         # Check existing product
#         # --------------------------------------------------------------------

#         product = db.scalar(
#             select(Product).where(
#                 Product.seller_id == DEMO_FARMER_ID,
#                 Product.name == name,
#             )
#         )

#         # --------------------------------------------------------------------
#         # IMPORTANT:
#         #
#         # If an existing product already has an image, keep it.
#         # Otherwise find a product-specific image.
#         # --------------------------------------------------------------------

#         if product is not None and product.image_url:

#             image_url = product.image_url

#             print(
#                 f"Using existing image: {name}"
#             )

#         else:

#             image_url = get_product_image(
#                 product_name=name,
#                 category_name=category_name,
#             )

#         # --------------------------------------------------------------------
#         # Image status
#         # --------------------------------------------------------------------

#         if image_url:

#             image_count += 1

#             print(
#                 f"Image assigned: {name}"
#             )

#         else:

#             missing_images.append(name)

#             print(
#                 f"WARNING: No image found: {name}"
#             )

#         # --------------------------------------------------------------------
#         # Product description
#         # --------------------------------------------------------------------

#         description = (
#             f"{'Organic' if organic else 'Natural'} "
#             f"{name}."
#         )

#         # --------------------------------------------------------------------
#         # CREATE
#         # --------------------------------------------------------------------

#         if product is None:

#             product = Product(
#                 seller_id=DEMO_FARMER_ID,
#                 category_id=category.id,
#                 name=name,
#                 description=description,
#                 price=Decimal(str(price)),
#                 stock_quantity=stock_quantity,
#                 unit=unit,
#                 certification="APPROVED",
#                 image_url=image_url,
#                 is_active=True,
#             )

#             db.add(product)

#             created += 1

#             print(
#                 f"Created product: {name}"
#             )

#         # --------------------------------------------------------------------
#         # UPDATE
#         # --------------------------------------------------------------------

#         else:

#             product.category_id = category.id
#             product.description = description
#             product.price = Decimal(str(price))
#             product.stock_quantity = stock_quantity
#             product.unit = unit
#             product.certification = "APPROVED"
#             product.is_active = True

#             # Only replace image if we successfully found one.
#             if image_url:
#                 product.image_url = image_url

#             updated += 1

#             print(
#                 f"Updated product: {name}"
#             )

#     return (
#         created,
#         updated,
#         image_count,
#         missing_images,
#     )


# # ============================================================================
# # VALIDATION
# # ============================================================================

# def validate_catalog():

#     product_count = len(PRODUCTS)

#     category_count = len(CATEGORIES)

#     print()
#     print("=" * 70)
#     print("CATALOG VALIDATION")
#     print("=" * 70)

#     print(
#         f"Categories defined : {category_count}"
#     )

#     print(
#         f"Products defined   : {product_count}"
#     )

#     if category_count != 9:

#         raise ValueError(
#             f"Expected 9 categories, "
#             f"found {category_count}"
#         )

#     if product_count != 200:

#         raise ValueError(
#             f"Expected exactly 200 products, "
#             f"found {product_count}"
#         )

#     # ------------------------------------------------------------------------
#     # Validate product categories
#     # ------------------------------------------------------------------------

#     valid_categories = {
#         name for name, _ in CATEGORIES
#     }

#     invalid_products = [
#         (
#             name,
#             category_name,
#         )
#         for (
#             name,
#             category_name,
#             price,
#             stock,
#             unit,
#             organic,
#             vendor,
#         ) in PRODUCTS
#         if category_name not in valid_categories
#     ]

#     if invalid_products:

#         print("\nInvalid products:")

#         for name, category_name in invalid_products:

#             print(
#                 f"  {name} -> {category_name}"
#             )

#         raise ValueError(
#             "One or more products contain "
#             "invalid categories."
#         )

#     # ------------------------------------------------------------------------
#     # Check duplicate product names
#     # ------------------------------------------------------------------------

#     names = [
#         product[0]
#         for product in PRODUCTS
#     ]

#     duplicates = {
#         name
#         for name in names
#         if names.count(name) > 1
#     }

#     if duplicates:

#         raise ValueError(
#             "Duplicate product names found: "
#             + ", ".join(sorted(duplicates))
#         )

#     print()
#     print("Catalog validation passed.")
#     print("=" * 70)


# # ============================================================================
# # IMAGE VALIDATION
# # ============================================================================

# def validate_product_images():
#     """Validate image mappings while allowing missing images (None)."""
#     product_names = {product[0] for product in PRODUCTS}
#     mapped_names = set(PRODUCT_IMAGES)

#     if mapped_names != product_names:
#         missing = sorted(product_names - mapped_names)
#         extra = sorted(mapped_names - product_names)
#         raise ValueError(f"Image mapping mismatch. Missing: {missing}; Extra: {extra}")

#     urls = [url for url in PRODUCT_IMAGES.values() if url]
#     duplicates = {url for url in urls if urls.count(url) > 1}
#     if duplicates:
#         raise ValueError("Duplicate non-null product image URLs detected:\n" + "\n".join(sorted(duplicates)))

#     print(f"Image mappings defined : {len(PRODUCT_IMAGES)}")
#     print(f"Unique seed image URLs : {len(urls)}")
#     print(f"Products with no image : {len(PRODUCT_IMAGES) - len(urls)}")
#     print("Image mapping validation passed.")


# # ============================================================================
# # MAIN
# # ============================================================================

# def main():

#     print("=" * 70)
#     print("OrganicKart Product Catalog Seed")
#     print("=" * 70)

#     # ------------------------------------------------------------------------
#     # Validate the hardcoded catalog BEFORE touching the database.
#     # ------------------------------------------------------------------------

#     validate_catalog()
#     validate_product_images()

#     # ------------------------------------------------------------------------
#     # Database session
#     # ------------------------------------------------------------------------

#     db = SessionLocal()

#     try:

#         # --------------------------------------------------------------------
#         # Categories
#         # --------------------------------------------------------------------

#         print()
#         print("Seeding categories...")

#         category_map = seed_categories(db)

#         # --------------------------------------------------------------------
#         # Products
#         # --------------------------------------------------------------------

#         print()
#         print("Seeding products...")

#         (
#             created,
#             updated,
#             image_count,
#             missing_images,
#         ) = seed_products(
#             db,
#             category_map,
#         )

#         # --------------------------------------------------------------------
#         # Commit
#         # --------------------------------------------------------------------

#         db.commit()

#         # --------------------------------------------------------------------
#         # Summary
#         # --------------------------------------------------------------------

#         print()
#         print("=" * 70)
#         print("SEED COMPLETE")
#         print("=" * 70)

#         print(
#             f"Categories          : {len(category_map)}"
#         )

#         print(
#             f"Products defined    : {len(PRODUCTS)}"
#         )

#         print(
#             f"Products created    : {created}"
#         )

#         print(
#             f"Products updated    : {updated}"
#         )

#         print(
#             f"Images assigned     : {image_count}"
#         )

#         print(
#             f"Images missing      : {len(missing_images)}"
#         )

#         print(
#             f"Seller ID           : {DEMO_FARMER_ID}"
#         )

#         # --------------------------------------------------------------------
#         # Missing images
#         # --------------------------------------------------------------------

#         if missing_images:

#             print()
#             print("Products without images:")

#             for product_name in missing_images:

#                 print(
#                     f"  - {product_name}"
#                 )

#         else:

#             print()
#             print(
#                 "SUCCESS: Seed image URLs are unique; products without images are ready for vendor upload."
#             )

#         print("=" * 70)

#     except Exception:

#         db.rollback()

#         raise

#     finally:

#         db.close()


# # ============================================================================
# # ENTRY POINT
# # ============================================================================

# if __name__ == "__main__":
#     main()

from decimal import Decimal

from sqlalchemy import select

from app.database.database import SessionLocal
from app.models.category import Category
from app.models.products import Product
from app.core.config import settings

# ============================================================================
# CONFIGURATION
# ============================================================================

DEMO_FARMER_ID = 1


# ============================================================================
# CATEGORY DATA
# ============================================================================

CATEGORIES = [
    ("Fruits", "Fresh, seasonal organic fruits."),
    ("Vegetables", "Farm-fresh organic vegetables."),
    ("Organic Oils", "Cold-pressed and unrefined organic oils."),
    ("Juices & Beverages", "Cold-pressed juices and organic beverages."),
    ("Grains & Pulses", "Organic grains, rice, and pulses."),
    ("Spices", "Sun-dried, chemical-free organic spices."),
    ("Snacks", "Healthy organic snacks and dry fruits."),
    ("Honey & Sweeteners", "Raw honey and natural sweeteners."),
    ("Personal Care", "Organic and natural personal care products."),
]

# ============================================================================
# PRODUCT DATA
#
# Tuple format:
# (
#     name,
#     category,
#     price,
#     stock_quantity,
#     unit,
#     organic,
#     vendor,
# )
# ============================================================================

PRODUCTS = [
    # ========================================================================
    # FRUITS - 25
    # ========================================================================

    ("Alphonso Mangoes", "Fruits", 450.00, 40, "kg", True, "Konkan Organic Farms"),
    ("Organic Bananas", "Fruits", 60.00, 120, "dozen", True, "Demo Organic Farms"),
    ("Fuji Apples", "Fruits", 220.00, 75, "kg", True, "Demo Organic Farms"),
    ("Kashmiri Apples", "Fruits", 240.00, 65, "kg", True, "Kashmir Organic Farms"),
    ("Kesar Mangoes", "Fruits", 380.00, 45, "kg", True, "Gujarat Organic Farms"),
    ("Organic Papaya", "Fruits", 70.00, 80, "kg", True, "Demo Organic Farms"),
    ("Fresh Pineapple", "Fruits", 90.00, 55, "piece", True, "Kerala Organic Farms"),
    ("Organic Watermelon", "Fruits", 45.00, 100, "kg", True, "Demo Organic Farms"),
    ("Green Grapes", "Fruits", 160.00, 70, "kg", True, "Maharashtra Farms"),
    ("Black Grapes", "Fruits", 190.00, 55, "kg", True, "Maharashtra Farms"),
    ("Organic Pomegranate", "Fruits", 260.00, 60, "kg", True, "Demo Organic Farms"),
    ("Sweet Lime", "Fruits", 90.00, 75, "kg", True, "Andhra Organic Farms"),
    ("Organic Oranges", "Fruits", 110.00, 90, "kg", True, "Nagpur Organic Farms"),
    ("Mosambi", "Fruits", 100.00, 80, "kg", True, "Maharashtra Farms"),
    ("Organic Guava", "Fruits", 85.00, 70, "kg", True, "Demo Organic Farms"),
    ("Dragon Fruit", "Fruits", 280.00, 45, "kg", True, "Karnataka Organic Farms"),
    ("Organic Kiwi", "Fruits", 350.00, 40, "kg", True, "Himalayan Organic Farms"),
    ("Fresh Strawberries", "Fruits", 320.00, 35, "box", True, "Mahabaleshwar Farms"),
    ("Organic Pears", "Fruits", 240.00, 55, "kg", True, "Himachal Organic Farms"),
    ("Custard Apple", "Fruits", 180.00, 50, "kg", True, "Karnataka Farms"),
    ("Organic Sapota", "Fruits", 100.00, 65, "kg", True, "Karnataka Organic Farms"),
    ("Fresh Coconut", "Fruits", 55.00, 120, "piece", True, "Kerala Organic Farms"),
    ("Tender Coconut", "Fruits", 70.00, 100, "piece", True, "Kerala Organic Farms"),
    ("Organic Plums", "Fruits", 260.00, 40, "kg", True, "Himachal Organic Farms"),
    ("Fresh Chikoo", "Fruits", 110.00, 60, "kg", True, "Maharashtra Farms"),

    # ========================================================================
    # VEGETABLES - 30
    # ========================================================================

    ("Organic Spinach", "Vegetables", 40.00, 60, "bunch", True, "Demo Organic Farms"),
    ("Heirloom Tomatoes", "Vegetables", 80.00, 90, "kg", True, "Demo Organic Farms"),
    ("Organic Carrots", "Vegetables", 55.00, 100, "kg", True, "Demo Organic Farms"),
    ("Organic Potatoes", "Vegetables", 45.00, 150, "kg", True, "Demo Organic Farms"),
    ("Organic Onions", "Vegetables", 50.00, 140, "kg", True, "Demo Organic Farms"),
    ("Green Capsicum", "Vegetables", 90.00, 75, "kg", True, "Karnataka Organic Farms"),
    ("Red Capsicum", "Vegetables", 140.00, 60, "kg", True, "Karnataka Organic Farms"),
    ("Yellow Capsicum", "Vegetables", 150.00, 55, "kg", True, "Karnataka Organic Farms"),
    ("Organic Cucumber", "Vegetables", 50.00, 100, "kg", True, "Demo Organic Farms"),
    ("Organic Beetroot", "Vegetables", 60.00, 80, "kg", True, "Demo Organic Farms"),
    ("Fresh Broccoli", "Vegetables", 120.00, 65, "kg", True, "Ooty Organic Farms"),
    ("Organic Cauliflower", "Vegetables", 80.00, 70, "kg", True, "Demo Organic Farms"),
    ("Organic Cabbage", "Vegetables", 45.00, 90, "kg", True, "Demo Organic Farms"),
    ("Green Beans", "Vegetables", 100.00, 70, "kg", True, "Karnataka Organic Farms"),
    ("French Beans", "Vegetables", 120.00, 55, "kg", True, "Karnataka Organic Farms"),
    ("Organic Green Peas", "Vegetables", 140.00, 50, "kg", True, "Himachal Organic Farms"),
    ("Lady Finger", "Vegetables", 75.00, 80, "kg", True, "Demo Organic Farms"),
    ("Organic Brinjal", "Vegetables", 65.00, 90, "kg", True, "Demo Organic Farms"),
    ("Bottle Gourd", "Vegetables", 55.00, 70, "piece", True, "Karnataka Organic Farms"),
    ("Ridge Gourd", "Vegetables", 70.00, 65, "kg", True, "Karnataka Organic Farms"),
    ("Bitter Gourd", "Vegetables", 80.00, 60, "kg", True, "Demo Organic Farms"),
    ("Drumstick", "Vegetables", 110.00, 50, "kg", True, "Tamil Nadu Organic Farms"),
    ("Sweet Corn", "Vegetables", 60.00, 85, "piece", True, "Karnataka Organic Farms"),
    ("Organic Pumpkin", "Vegetables", 55.00, 60, "kg", True, "Demo Organic Farms"),
    ("Radish", "Vegetables", 45.00, 75, "kg", True, "Demo Organic Farms"),
    ("Turnip", "Vegetables", 70.00, 55, "kg", True, "Himachal Organic Farms"),
    ("Organic Fenugreek Leaves", "Vegetables", 35.00, 70, "bunch", True, "Demo Organic Farms"),
    ("Coriander Leaves", "Vegetables", 30.00, 100, "bunch", True, "Demo Organic Farms"),
    ("Curry Leaves", "Vegetables", 35.00, 90, "bunch", True, "Karnataka Organic Farms"),
    ("Organic Garlic", "Vegetables", 90.00, 80, "kg", True, "Karnataka Organic Farms"),
    # ========================================================================
    # ORGANIC OILS - 20
    # ========================================================================

    ("Cold-Pressed Coconut Oil", "Organic Oils", 320.00, 50, "litre", True, "Kerala Organic Oils"),
    ("Cold-Pressed Groundnut Oil", "Organic Oils", 280.00, 45, "litre", True, "Demo Organic Farms"),
    ("Cold-Pressed Sesame Oil", "Organic Oils", 360.00, 40, "litre", True, "Tamil Nadu Organic Farms"),
    ("Cold-Pressed Mustard Oil", "Organic Oils", 300.00, 45, "litre", True, "Rajasthan Organic Farms"),
    ("Organic Sunflower Oil", "Organic Oils", 260.00, 55, "litre", True, "Karnataka Organic Farms"),
    ("Organic Safflower Oil", "Organic Oils", 340.00, 35, "litre", True, "Maharashtra Farms"),
    ("Cold-Pressed Flaxseed Oil", "Organic Oils", 650.00, 30, "litre", True, "Himalayan Organic Farms"),
    ("Cold-Pressed Avocado Oil", "Organic Oils", 850.00, 25, "litre", True, "Organic Valley Farms"),
    ("Organic Olive Oil", "Organic Oils", 750.00, 40, "litre", True, "Indian Organic Oils"),
    ("Extra Virgin Olive Oil", "Organic Oils", 900.00, 30, "litre", True, "Indian Organic Oils"),
    ("Organic Rice Bran Oil", "Organic Oils", 290.00, 50, "litre", True, "Demo Organic Farms"),
    ("Cold-Pressed Walnut Oil", "Organic Oils", 780.00, 20, "litre", True, "Himachal Organic Farms"),
    ("Cold-Pressed Almond Oil", "Organic Oils", 950.00, 25, "litre", True, "Rajasthan Organic Farms"),
    ("Organic Sesame Cooking Oil", "Organic Oils", 380.00, 45, "litre", True, "Tamil Nadu Organic Farms"),
    ("Virgin Coconut Oil", "Organic Oils", 420.00, 40, "litre", True, "Kerala Organic Oils"),
    ("Organic Hemp Seed Oil", "Organic Oils", 1100.00, 15, "litre", True, "Organic Valley Farms"),
    ("Cold-Pressed Castor Oil", "Organic Oils", 260.00, 35, "litre", True, "Rajasthan Organic Farms"),
    ("Organic Moringa Oil", "Organic Oils", 900.00, 20, "litre", True, "Tamil Nadu Organic Farms"),
    ("Cold-Pressed Neem Oil", "Organic Oils", 350.00, 30, "litre", True, "Karnataka Organic Farms"),
    ("Organic Mustard Seed Oil", "Organic Oils", 310.00, 45, "litre", True, "Rajasthan Organic Farms"),

    # ========================================================================
    # JUICES & BEVERAGES - 20
    # ========================================================================

    ("Fresh Sugarcane Juice Concentrate", "Juices & Beverages", 150.00, 30, "litre", False, None),
    ("Organic Amla Juice", "Juices & Beverages", 180.00, 35, "litre", True, "Demo Organic Farms"),
    ("Organic Mango Juice", "Juices & Beverages", 220.00, 40, "litre", True, "Konkan Organic Farms"),
    ("Organic Orange Juice", "Juices & Beverages", 190.00, 45, "litre", True, "Nagpur Organic Farms"),
    ("Organic Apple Juice", "Juices & Beverages", 240.00, 35, "litre", True, "Himachal Organic Farms"),
    ("Organic Pomegranate Juice", "Juices & Beverages", 280.00, 30, "litre", True, "Demo Organic Farms"),
    ("Organic Pineapple Juice", "Juices & Beverages", 210.00, 40, "litre", True, "Kerala Organic Farms"),
    ("Organic Guava Juice", "Juices & Beverages", 180.00, 35, "litre", True, "Demo Organic Farms"),
    ("Tender Coconut Water", "Juices & Beverages", 120.00, 60, "litre", True, "Kerala Organic Farms"),
    ("Organic Lemon Ginger Drink", "Juices & Beverages", 160.00, 50, "litre", True, "Demo Organic Farms"),
    ("Organic Beetroot Juice", "Juices & Beverages", 200.00, 35, "litre", True, "Karnataka Organic Farms"),
    ("Organic Carrot Juice", "Juices & Beverages", 190.00, 40, "litre", True, "Demo Organic Farms"),
    ("Organic Mixed Fruit Juice", "Juices & Beverages", 230.00, 45, "litre", True, "Demo Organic Farms"),
    ("Organic Kokum Juice", "Juices & Beverages", 220.00, 30, "litre", True, "Konkan Organic Farms"),
    ("Organic Jamun Juice", "Juices & Beverages", 250.00, 25, "litre", True, "Karnataka Organic Farms"),
    ("Organic Wheatgrass Juice", "Juices & Beverages", 320.00, 20, "litre", True, "Demo Organic Farms"),
    ("Organic Tulsi Herbal Drink", "Juices & Beverages", 180.00, 40, "litre", True, "Demo Organic Farms"),
    ("Organic Cucumber Mint Juice", "Juices & Beverages", 170.00, 35, "litre", True, "Karnataka Organic Farms"),
    ("Organic Aloe Vera Drink", "Juices & Beverages", 200.00, 30, "litre", True, "Demo Organic Farms"),
    ("Organic Ginger Lemonade", "Juices & Beverages", 150.00, 50, "litre", True, "Demo Organic Farms"),

    # ========================================================================
    # GRAINS & PULSES - 25
    # ========================================================================

    ("Organic Brown Rice", "Grains & Pulses", 95.00, 200, "kg", True, "Demo Organic Farms"),
    ("Organic Toor Dal", "Grains & Pulses", 140.00, 150, "kg", True, "Demo Organic Farms"),
    ("Organic Basmati Rice", "Grains & Pulses", 180.00, 120, "kg", True, "Punjab Organic Farms"),
    ("Organic Sona Masoori Rice", "Grains & Pulses", 110.00, 180, "kg", True, "Karnataka Organic Farms"),
    ("Organic Red Rice", "Grains & Pulses", 130.00, 100, "kg", True, "Kerala Organic Farms"),
    ("Organic Black Rice", "Grains & Pulses", 220.00, 70, "kg", True, "Northeast Organic Farms"),
    ("Organic Quinoa", "Grains & Pulses", 360.00, 60, "kg", True, "Organic Valley Farms"),
    ("Organic Foxtail Millet", "Grains & Pulses", 140.00, 90, "kg", True, "Karnataka Organic Farms"),
    ("Organic Finger Millet", "Grains & Pulses", 100.00, 120, "kg", True, "Karnataka Organic Farms"),
    ("Organic Pearl Millet", "Grains & Pulses", 95.00, 100, "kg", True, "Rajasthan Organic Farms"),
    ("Organic Little Millet", "Grains & Pulses", 150.00, 70, "kg", True, "Karnataka Organic Farms"),
    ("Organic Kodo Millet", "Grains & Pulses", 145.00, 65, "kg", True, "Madhya Pradesh Farms"),
    ("Organic Barnyard Millet", "Grains & Pulses", 160.00, 60, "kg", True, "Karnataka Organic Farms"),
    ("Organic Green Moong Dal", "Grains & Pulses", 150.00, 120, "kg", True, "Demo Organic Farms"),
    ("Organic Black Urad Dal", "Grains & Pulses", 170.00, 100, "kg", True, "Demo Organic Farms"),
    ("Organic Chana Dal", "Grains & Pulses", 125.00, 140, "kg", True, "Rajasthan Organic Farms"),
    ("Organic Masoor Dal", "Grains & Pulses", 135.00, 130, "kg", True, "Madhya Pradesh Farms"),
    ("Organic Kabuli Chana", "Grains & Pulses", 160.00, 100, "kg", True, "Rajasthan Organic Farms"),
    ("Organic Rajma", "Grains & Pulses", 190.00, 90, "kg", True, "Himachal Organic Farms"),
    ("Organic Black Chana", "Grains & Pulses", 120.00, 110, "kg", True, "Rajasthan Organic Farms"),
    ("Organic Green Gram", "Grains & Pulses", 145.00, 100, "kg", True, "Karnataka Organic Farms"),
    ("Organic Red Kidney Beans", "Grains & Pulses", 180.00, 80, "kg", True, "Himachal Organic Farms"),
    ("Organic Barley", "Grains & Pulses", 90.00, 100, "kg", True, "Punjab Organic Farms"),
    ("Organic Rolled Oats", "Grains & Pulses", 180.00, 90, "kg", True, "Organic Valley Farms"),
    ("Organic Broken Wheat", "Grains & Pulses", 85.00, 120, "kg", True, "Punjab Organic Farms"),

    # ========================================================================
    # SPICES - 25
    # ========================================================================

    ("Organic Turmeric Powder", "Spices", 90.00, 80, "kg", True, "Demo Organic Farms"),
    ("Organic Black Pepper", "Spices", 480.00, 25, "kg", True, "Kerala Organic Oils"),
    ("Organic Cumin Seeds", "Spices", 360.00, 40, "kg", True, "Rajasthan Organic Farms"),
    ("Organic Coriander Powder", "Spices", 180.00, 55, "kg", True, "Rajasthan Organic Farms"),
    ("Organic Red Chilli Powder", "Spices", 220.00, 50, "kg", True, "Andhra Organic Farms"),
    ("Organic Green Cardamom", "Spices", 1800.00, 15, "kg", True, "Kerala Organic Farms"),
    ("Organic Cloves", "Spices", 1100.00, 20, "kg", True, "Kerala Organic Farms"),
    ("Organic Cinnamon", "Spices", 700.00, 25, "kg", True, "Kerala Organic Farms"),
    ("Organic Fennel Seeds", "Spices", 250.00, 35, "kg", True, "Rajasthan Organic Farms"),
    ("Organic Fenugreek Seeds", "Spices", 180.00, 40, "kg", True, "Rajasthan Organic Farms"),
    ("Organic Mustard Seeds", "Spices", 140.00, 45, "kg", True, "Rajasthan Organic Farms"),
    ("Organic Ajwain", "Spices", 300.00, 30, "kg", True, "Rajasthan Organic Farms"),
    ("Organic Bay Leaves", "Spices", 450.00, 20, "kg", True, "Kerala Organic Farms"),
    ("Organic Star Anise", "Spices", 900.00, 15, "kg", True, "Northeast Organic Farms"),
    ("Organic Nutmeg", "Spices", 1000.00, 18, "kg", True, "Kerala Organic Farms"),
    ("Organic Mace", "Spices", 1500.00, 12, "kg", True, "Kerala Organic Farms"),
    ("Organic Dry Ginger", "Spices", 380.00, 25, "kg", True, "Kerala Organic Farms"),
    ("Organic Asafoetida", "Spices", 1200.00, 15, "kg", True, "Demo Organic Farms"),
    ("Organic Garam Masala", "Spices", 300.00, 40, "kg", True, "Demo Organic Farms"),
    ("Organic Sambar Powder", "Spices", 280.00, 45, "kg", True, "Karnataka Organic Farms"),
    ("Organic Rasam Powder", "Spices", 290.00, 40, "kg", True, "Karnataka Organic Farms"),
    ("Organic Curry Powder", "Spices", 320.00, 35, "kg", True, "Kerala Organic Farms"),
    ("Organic Chaat Masala", "Spices", 280.00, 30, "kg", True, "Rajasthan Organic Farms"),
    ("Organic Kashmiri Chilli Powder", "Spices", 400.00, 25, "kg", True, "Kashmir Organic Farms"),
    ("Organic Panch Phoron", "Spices", 250.00, 30, "kg", True, "West Bengal Organic Farms"),

    # ========================================================================
    # SNACKS - 25
    # ========================================================================

    ("Roasted Makhana (Fox Nuts)", "Snacks", 260.00, 60, "kg", False, None),
    ("Mixed Dry Fruit Trail Mix", "Snacks", 350.00, 40, "kg", False, None),
    ("Organic Almonds", "Snacks", 850.00, 50, "kg", True, "Kashmir Organic Farms"),
    ("Organic Cashews", "Snacks", 900.00, 45, "kg", True, "Goa Organic Farms"),
    ("Organic Walnuts", "Snacks", 950.00, 35, "kg", True, "Kashmir Organic Farms"),
    ("Organic Raisins", "Snacks", 420.00, 55, "kg", True, "Maharashtra Farms"),
    ("Organic Dates", "Snacks", 500.00, 60, "kg", True, "Organic Valley Farms"),
    ("Organic Pistachios", "Snacks", 1100.00, 30, "kg", True, "Organic Valley Farms"),
    ("Roasted Chickpeas", "Snacks", 220.00, 70, "kg", True, "Rajasthan Organic Farms"),
    ("Organic Peanut Chikki", "Snacks", 280.00, 60, "kg", True, "Karnataka Organic Farms"),
    ("Organic Sesame Chikki", "Snacks", 300.00, 50, "kg", True, "Karnataka Organic Farms"),
    ("Organic Jowar Puffs", "Snacks", 180.00, 65, "kg", True, "Maharashtra Farms"),
    ("Organic Ragi Chips", "Snacks", 220.00, 60, "kg", True, "Karnataka Organic Farms"),
    ("Organic Banana Chips", "Snacks", 240.00, 70, "kg", True, "Kerala Organic Farms"),
    ("Organic Jackfruit Chips", "Snacks", 280.00, 50, "kg", True, "Kerala Organic Farms"),
    ("Organic Sweet Potato Chips", "Snacks", 260.00, 45, "kg", True, "Karnataka Organic Farms"),
    ("Organic Millet Cookies", "Snacks", 320.00, 50, "kg", True, "Demo Organic Farms"),
    ("Organic Oat Cookies", "Snacks", 300.00, 55, "kg", True, "Demo Organic Farms"),
    ("Organic Coconut Cookies", "Snacks", 340.00, 40, "kg", True, "Kerala Organic Farms"),
    ("Organic Granola", "Snacks", 450.00, 35, "kg", True, "Organic Valley Farms"),
    ("Organic Trail Mix", "Snacks", 500.00, 40, "kg", True, "Organic Valley Farms"),
    ("Roasted Pumpkin Seeds", "Snacks", 650.00, 30, "kg", True, "Organic Valley Farms"),
    ("Roasted Sunflower Seeds", "Snacks", 450.00, 35, "kg", True, "Organic Valley Farms"),
    ("Organic Coconut Chips", "Snacks", 380.00, 40, "kg", True, "Kerala Organic Farms"),
    ("Organic Murukku", "Snacks", 320.00, 45, "kg", True, "Karnataka Organic Farms"),

    # ========================================================================
    # HONEY & SWEETENERS - 15
    # ========================================================================

    ("Raw Forest Honey", "Honey & Sweeteners", 420.00, 55, "kg", True, "Demo Organic Farms"),
    ("Organic Jaggery", "Honey & Sweeteners", 85.00, 100, "kg", True, "Demo Organic Farms"),
    ("Organic Jaggery Powder", "Honey & Sweeteners", 110.00, 90, "kg", True, "Karnataka Organic Farms"),
    ("Raw Multifloral Honey", "Honey & Sweeteners", 450.00, 50, "kg", True, "Demo Organic Farms"),
    ("Organic Wildflower Honey", "Honey & Sweeteners", 480.00, 45, "kg", True, "Himalayan Organic Farms"),
    ("Organic Acacia Honey", "Honey & Sweeteners", 550.00, 35, "kg", True, "Organic Valley Farms"),
    ("Organic Neem Honey", "Honey & Sweeteners", 500.00, 30, "kg", True, "Karnataka Organic Farms"),
    ("Organic Jamun Honey", "Honey & Sweeteners", 520.00, 30, "kg", True, "Karnataka Organic Farms"),
    ("Organic Date Syrup", "Honey & Sweeteners", 450.00, 35, "litre", True, "Organic Valley Farms"),
    ("Organic Coconut Sugar", "Honey & Sweeteners", 380.00, 40, "kg", True, "Kerala Organic Farms"),
    ("Organic Palm Jaggery", "Honey & Sweeteners", 180.00, 60, "kg", True, "Tamil Nadu Organic Farms"),
    ("Organic Cane Sugar", "Honey & Sweeteners", 120.00, 80, "kg", True, "Karnataka Organic Farms"),
    ("Organic Stevia Powder", "Honey & Sweeteners", 650.00, 25, "kg", True, "Organic Valley Farms"),
    ("Organic Maple Syrup", "Honey & Sweeteners", 900.00, 25, "litre", True, "Organic Valley Farms"),
    ("Organic Agave Syrup", "Honey & Sweeteners", 700.00, 25, "litre", True, "Organic Valley Farms"),

    # ========================================================================
    # PERSONAL CARE - 15
    # ========================================================================

    ("Organic Aloe Vera Gel", "Personal Care", 199.00, 70, "piece", True, "Demo Organic Farms"),
    ("Herbal Neem Soap", "Personal Care", 60.00, 150, "piece", False, None),
    ("Organic Turmeric Soap", "Personal Care", 75.00, 100, "piece", True, "Demo Organic Farms"),
    ("Organic Sandalwood Soap", "Personal Care", 110.00, 80, "piece", True, "Karnataka Organic Farms"),
    ("Organic Coconut Soap", "Personal Care", 80.00, 90, "piece", True, "Kerala Organic Farms"),
    ("Organic Rose Face Wash", "Personal Care", 220.00, 60, "piece", True, "Demo Organic Farms"),
    ("Organic Neem Face Wash", "Personal Care", 210.00, 65, "piece", True, "Demo Organic Farms"),
    ("Organic Aloe Face Wash", "Personal Care", 230.00, 60, "piece", True, "Demo Organic Farms"),
    ("Organic Coconut Shampoo", "Personal Care", 280.00, 55, "piece", True, "Kerala Organic Farms"),
    ("Organic Hibiscus Shampoo", "Personal Care", 300.00, 50, "piece", True, "Karnataka Organic Farms"),
    ("Organic Amla Hair Oil", "Personal Care", 260.00, 60, "piece", True, "Demo Organic Farms"),
    ("Organic Coconut Hair Oil", "Personal Care", 240.00, 70, "piece", True, "Kerala Organic Farms"),
    ("Organic Rose Water", "Personal Care", 180.00, 75, "piece", True, "Rajasthan Organic Farms"),
    ("Organic Neem Powder", "Personal Care", 160.00, 50, "kg", True, "Karnataka Organic Farms"),
    ("Organic Multani Mitti", "Personal Care", 140.00, 60, "kg", True, "Rajasthan Organic Farms"),
]


# ============================================================================
# DEMO / SEED PRODUCT IMAGES
#
# Seed images are optional. Products without a verified seed image use None.
# Duplicate image URLs from the previous mapping were removed.
# Vendor-uploaded images can replace these values later.
# ============================================================================

PRODUCT_IMAGES = {
    'Alphonso Mangoes': 'https://images.unsplash.com/photo-1553279768-865429fa0078?auto=format&fit=crop&w=900&q=85',
    'Organic Bananas': 'https://images.unsplash.com/photo-1571771894821-ce9b6c11b08e?auto=format&fit=crop&w=900&q=85',
    'Fuji Apples': 'https://www.saudifruit.sa/images/products-new/Fuji-Apples.jpg',
    'Kashmiri Apples': 'https://cf-img-a-in.tosshub.com/sites/visualstory/wp/2025/04/Kashmiri-ApplesITG-1745658119536.webp?size=%2A%3A900',
    'Kesar Mangoes': 'https://www.mangodatabase.com/images/varieties/whc65b65037d718f_f5QYmDjJYY_S212HU5oUr.jpg',
    'Organic Papaya': 'https://images.unsplash.com/photo-1556719240-31629484142a?auto=format&fit=crop&w=900&q=85',
    'Fresh Pineapple': 'https://upload.wikimedia.org/wikipedia/commons/9/9c/Fresh_Pineapple_Fruits.jpg',
    'Organic Watermelon': 'https://upload.wikimedia.org/wikipedia/commons/b/b9/Watermelon.jpg',
    'Green Grapes': 'https://cdn.salla.sa/apBzl/l18qeaR39amloRUWuQKfkNuBxmU79xYxhpSrWOlP.jpg',
    'Black Grapes': 'https://upload.wikimedia.org/wikipedia/commons/a/a7/Black_grapes_in_a_bowl.jpg',
    'Organic Pomegranate': 'https://tiimg.tistatic.com/fp/1/008/340/sweet-delicious-taste-natural-round-organic-pomegranate-299.jpg',
    'Sweet Lime': 'https://commons.wikimedia.org/wiki/Special:Redirect/file/%22Sweet_lime_of_Salem%22.jpg',
    'Organic Oranges': 'https://sgwetmarket.com.sg/cdn/shop/products/2.orange-navel-313149.jpg?v=1593132715',
    'Mosambi': 'https://commons.wikimedia.org/wiki/Special:Redirect/file/(Citrus%20limetta)%20Mosambi%20at%20a%20market%20in%20Seethammadhara.jpg',
    'Organic Guava': 'https://www.agroexporters.net/uploaded-files/thumb-cache/member_127/thumb---guava_4999.jpg',
    'Dragon Fruit': 'https://img.clevup.in/278008/SKU-0195_0-1720803662130.jpg?format=webp&width=600',
    'Organic Kiwi': 'https://images.unsplash.com/photo-1539461007403-49f413d10b64?auto=format&fit=crop&w=900&q=85',
    'Fresh Strawberries': 'https://www.ars.usda.gov/ARSUserFiles/oc/images/photos/featuredphoto/aug23/D3073-1w.jpg',
    'Organic Pears': 'https://d2j6dbq0eux0bg.cloudfront.net/images/7152101/2379575823.jpg',
    'Custard Apple': 'https://pluckk.s3.ap-south-1.amazonaws.com/uploads/3153-untitled-design-61.jpg',
    'Organic Sapota': 'https://static.wixstatic.com/media/1536ae_98951bff631244c58fd8971e2857a88e~mv2.jpg/v1/fit/w_500%2Ch_500%2Cq_90/file.jpg',
    'Fresh Coconut': 'https://www.metro-online.pk/_next/image?q=75&url=https%3A%2F%2Fprodimages.metro-online.pk%2FProducts%2F1689767373521.jpg&w=3840',
    'Tender Coconut': 'https://commons.wikimedia.org/wiki/Special:Redirect/file/Tender_coconut.jpg',
    'Organic Plums': 'https://i1.pickpik.com/photos/126/714/474/plum-fruit-fruits-violet-purple-preview.jpg',
    'Fresh Chikoo': 'https://services.kpnfresh.com/media/v1/products/images/09e3b8d5-2f6e-4194-955b-3f723479718e/chikoo.webp?c_type=C2',
    'Organic Spinach': 'https://images.unsplash.com/photo-1576045057995-568f588f82fb?auto=format&fit=crop&w=900&q=85',
    'Heirloom Tomatoes': 'https://images.unsplash.com/photo-1546094096-0df4bcaaa337?auto=format&fit=crop&w=900&q=85',
    'Organic Carrots': 'https://images.unsplash.com/photo-1445282768818-728615cc910a?auto=format&fit=crop&w=900&q=85',
    'Organic Potatoes': 'https://images.unsplash.com/photo-1508313880080-c4bef0730395?auto=format&fit=crop&w=900&q=85',
    'Organic Onions': 'https://commons.wikimedia.org/wiki/Special:Redirect/file/Onion%20or%20Allium%20cepa.jpg',
    'Green Capsicum': 'http://www.public-domain-image.com/full-image/flora-plants-public-domain-images-pictures/vegetables-public-domain-images-pictures/pepper-pictures/green-capsicum.jpg',
    'Red Capsicum': 'https://paddocktopantry.co.nz/cdn/shop/products/redcapsicum_900x.jpg?v=1693345796',
    'Yellow Capsicum': 'https://fruitworld.co.nz/cdn/shop/products/yellow_capsicum_pepper.png?v=1606363843&width=1000',
    'Organic Cucumber': 'https://images.unsplash.com/photo-1523349462262-054f5b3aa500?auto=format&fit=crop&w=900&q=85',
    'Organic Beetroot': 'https://organicbazar.net/cdn/shop/products/Beetroot-Seeds-2.jpg?v=1694167537',
    'Fresh Broccoli': 'https://images.unsplash.com/photo-1518164147695-36c13dd568f5?auto=format&fit=crop&w=900&q=85',
    'Organic Cauliflower': 'https://images.unsplash.com/photo-1558108722-d672acd746b8?auto=format&fit=crop&w=900&q=85',
    'Organic Cabbage': 'https://superbhyper.co.za/wp-content/uploads/2023/06/CABBAGE.jpg',
    'Green Beans': 'https://www.podtatranskadebnicka.sk/application/layouts/product-images/100/100-202.jpg',
    'French Beans': 'https://dukaan.b-cdn.net/500x500/webp/4075118/f9265ecb-b431-4f32-8deb-435b516c6d0c/french-beans1-56bfad07-42eb-4e15-9d2e-acf00f34ce8a.jpg',
    'Organic Green Peas': 'https://www.kibsons.com/_next/image?q=90&url=https%3A%2F%2Fcdn.kibsons.com%2Fproducts%2Fdetail%2FHPL_PEAGRPKXX04KA1_20251208115708.jpg&w=640',
    'Lady Finger': 'https://msosi.jumlajumla.com/_next/image?q=75&url=https%3A%2F%2Fmsosijumla.s3.eu-north-1.amazonaws.com%2Fpublic%2Fimages%2Fproducts%2F122-17459167781772.webp&w=3840',
    'Organic Brinjal': 'https://images.unsplash.com/photo-1647134619933-452c43b63970?auto=format&fit=crop&w=900&q=85',
    'Bottle Gourd': 'https://commons.wikimedia.org/wiki/Special:Redirect/file/Bottle%20Gourd.jpg',
    'Ridge Gourd': 'https://commons.wikimedia.org/wiki/Special:Redirect/file/Ridge%20Gourd.jpg',
    'Bitter Gourd': 'https://eshop.supernature.com.sg/cdn/shop/files/Bitter_gourd_1200x1200.jpg?v=1747106645',
    'Drumstick': 'https://toronto.motherlandgrocery.ca/cdn/shop/products/11503.png?v=1614908550',
    'Sweet Corn': 'https://www.bastanastore.com/cdn/shop/products/sweetcorn.jpg?v=1611047027',
    'Organic Pumpkin': 'https://cdn.hstatic.net/products/200000692807/bi_do_4dc1a183575040499832240426b1dc5e_master.png',
    'Radish': 'https://images.mathem.se/prod/local_products/c81f09a7-4323-4961-975f-485427b6bff8.jpg?fit=bounds&format=auto&optimize=medium&s=0xef25f48d3a4da6a2d3d1b1de87eaa5a69b099084&width=1000',
    'Turnip': 'https://commons.wikimedia.org/wiki/Special:Redirect/file/Turnips.jpg',
    'Organic Fenugreek Leaves': 'https://image.cdn.shpy.in/372001/SKU-0339_2-1730532147044.jpg?format=webp',
    'Coriander Leaves': 'https://joualvert.ca/cdn/shop/products/coriander_bb8d7913-fd8b-432e-a7b3-9e8561dbc823.jpg?v=1698701297',
    'Curry Leaves': 'https://www.asiatischer-lebensmittelladen.de/wp-content/uploads/2024/02/fresh-curry-leaves-isolated-on-600nw-1383411830.jpg.jpg',
    'Organic Garlic': 'https://untamedearth.nz/cdn/shop/products/WhatsAppImage2022-12-01at2.57.29PM_grande.jpg?v=1669860631',
    'Cold-Pressed Coconut Oil': 'https://www.bbassets.com/media/uploads/p/l/40359966_1-saffola-cold-pressed-coconut-oil.jpg',
    'Cold-Pressed Groundnut Oil': 'https://organicindia.com/cdn/shop/files/GroundnutOil1LtrBottle.png?v=1765865678&width=416',
    'Cold-Pressed Sesame Oil': 'https://excellafoods.com/cdn/shop/files/coldpresssesameoilcanvaedit.png?v=1738312913&width=500',
    'Cold-Pressed Mustard Oil': 'https://www.jiomart.com/images/product/original/494626147/saffola-cold-pressed-mustard-oil-1-l-product-images-o494626147-p612062510-0-202507301829.jpg?im=Resize%3D%281000%2C1000%29',
    'Organic Sunflower Oil': 'https://static.ah.nl/dam/product/AHI_434d50313036313232?fileType=binary&rendition=800x800_JPG_Q90&revLabel=3',
    'Organic Safflower Oil': 'https://lamoisson.com/cdn/shop/files/natur-huile-de-carthame-450ml.jpg?v=1752863776',
    'Cold-Pressed Flaxseed Oil': 'https://sunshinemarket.co.th/cdn/shop/files/Untitled-1-1.png?v=1722836486',
    'Cold-Pressed Avocado Oil': 'https://cdn.mafrservices.com/sys-master-root/ha9/hd1/35171081289758/1657615_main.jpg',
    'Organic Olive Oil': 'https://media-stark.gourmetmarketthailand.com/products/thumbnail/8859414000395-1.webp',
    'Extra Virgin Olive Oil': 'https://commons.wikimedia.org/wiki/Special:Redirect/file/Oliven%C3%B6l_extra_%2802%29.jpg',
    'Organic Rice Bran Oil': 'https://sg-live-01.slatic.net/p/f223a03b20da421a05fed6e7259a571a.jpg',
    'Cold-Pressed Walnut Oil': 'https://www.bestofhungary.co.uk/cdn/shop/files/OrganicWalnutOil250ml.jpg?v=1697444585&width=1214',
    'Cold-Pressed Almond Oil': 'https://www.niharti.com/image/cache/catalog/almond-oil-1l-700x700.jpg',
    'Organic Sesame Cooking Oil': 'https://commons.wikimedia.org/wiki/Special:Redirect/file/Sesame_oil.jpg',
    'Virgin Coconut Oil': 'https://www.sutrakart.com/cdn/shop/files/Pure_Cold_Pressed_Virgin_Coconut_Oil.png?v=1775559484',
    'Organic Hemp Seed Oil': 'https://www.gagneensante.com/cdn/shop/products/huile-de-chanvre-biologique-624004.png?v=1762533776',
    'Cold-Pressed Castor Oil': 'https://d2j6dbq0eux0bg.cloudfront.net/images/63607701/products/624408487/5522357313.jpg',
    'Organic Moringa Oil': 'https://i5.walmartimages.com/seo/Plantlife-Moringa-Carrier-Oil-Cold-Pressed-Non-GMO-and-Gluten-Free-Carrier-Oils-For-Skin-Hair-and-Personal-Care-2-oz_eeed09fe-f279-44db-9bd8-c22382d8e897.1b97cadf537b5d072e088be8a35408da.jpeg',
    'Cold-Pressed Neem Oil': 'https://puroestadofisico.com/cdn/shop/files/Best-Naturals-Aceite-De-Neem-473ml_800x.jpg?v=1710888139',
    'Organic Mustard Seed Oil': 'https://upload.wikimedia.org/wikipedia/commons/f/ff/Mustard_Oil_MoteNyinSei.jpg',
    'Fresh Sugarcane Juice Concentrate': 'https://images.unsplash.com/photo-1622597467836-f3285f2131b8?auto=format&fit=crop&w=900&q=85',
    'Organic Amla Juice': 'https://commons.wikimedia.org/wiki/Special:Redirect/file/Amla_juice.jpg',
    'Organic Mango Juice': 'https://matjrah.online/images/1404/image/cache/catalog/1692707173-8-1100x1100.jpg',
    'Organic Orange Juice': 'https://upload.wikimedia.org/wikipedia/commons/0/05/Orangejuice.jpg',
    'Organic Apple Juice': 'https://dg6qn11ynnp6a.cloudfront.net/wp-content/uploads/2023/04/04105423/632856345.martinelli.s.1l.organic-scaled.jpg',
    'Organic Pomegranate Juice': 'https://damassupermarket.com/2269-large_default/red-crown-organic-pomegranate-juice-1l-.jpg',
    'Organic Pineapple Juice': 'https://orderacme.s3.amazonaws.com/ProductImages/00074682107340.full.jpg',
    'Organic Guava Juice': 'https://upload.wikimedia.org/wikipedia/commons/3/33/Fresh_Gvava_Juice.JPG',
    'Tender Coconut Water': 'https://www.pinoygrocers.com/cdn/shop/files/ee9a6f9f-1668-488e-9fd9-fe1eb6ecfe97_8906009300566_018af5f8-f51a-42d6-a15c-c4c4a49f9251.webp?v=1765823119',
    'Organic Lemon Ginger Drink': 'https://upload.wikimedia.org/wikipedia/commons/2/28/A_boiled_Lemon_and_ginger_tea.jpg',
    'Organic Beetroot Juice': 'https://www.realfoods.co.uk/ProductImagesID/3389_1.jpg',
    'Organic Carrot Juice': 'https://cdn.salla.sa/RAxnwP/f0885e4c-bc6f-4492-9b4e-82f684698178-1000x1000-IuaL2pz135fOUnkRTrb3BnCVoKjnnie30ISxi4KL.png',
    'Organic Mixed Fruit Juice': 'https://upload.wikimedia.org/wikipedia/commons/b/ba/Mixture_of_fruit_juices.jpg',
    'Organic Kokum Juice': 'https://upload.wikimedia.org/wikipedia/commons/0/08/Kokum_or_Punarpuli_sharbat.jpg',
    'Organic Jamun Juice': 'https://freshmills.in/cdn/shop/files/organic-jamun-juice-867719.jpg?v=1717362174&width=1500',
    'Organic Wheatgrass Juice': 'https://vinut.com.vn/wp-content/webp-express/webp-images/uploads/2019/12/300ml_Bottled_WheatGrass_Juice_Drink_Original-600x600.jpg.webp',
    'Organic Tulsi Herbal Drink': 'https://upload.wikimedia.org/wikipedia/commons/0/0d/Tulsi_Tea.JPG',
    'Organic Cucumber Mint Juice': 'https://i.ebayimg.com/images/g/5PIAAOSwdsVmbP0R/s-l1200.jpg',
    'Organic Aloe Vera Drink': 'https://cdnprod.mafretailproxy.com/sys-master-root/h23/ha1/26758313803806/748853_main.jpg_480Wx480H',
    'Organic Ginger Lemonade': 'https://upload.wikimedia.org/wikipedia/commons/d/d4/Ginger_Lemon_Fizz.JPG',
    'Organic Brown Rice': 'https://i5.walmartimages.com/asr/b17e9da2-9904-49f2-882b-f3debd34e657_1.224a11ad9cef553c3124da53a21c821d.jpeg?odnBg=ffffff&odnHeight=1000&odnWidth=1000',
    'Organic Toor Dal': 'https://i5.walmartimages.com/seo/Sheel-Organic-Toor-Dal-Split-Pigeon-Pea-4-lbs_59d26111-dd40-44e1-bb08-aefcf7d8c87a.da1f04f304491caa1fe128aa35ca0895.jpeg?odnBg=FFFFFF&odnHeight=768&odnWidth=768',
    'Organic Basmati Rice': 'https://img3.21food.com/img/product/2020/11/19/food3052421605749450953875.jpg',
    'Organic Sona Masoori Rice': 'https://www.thefastrack.co.uk/uploads/products/view/1745176259.jpg',
    'Organic Red Rice': 'https://www.ecohoy.com/media/catalog/product/cache/1/thumbnail/600x/9df78eab33525d08d6e5fb8d27136e95/O/r/OrganicsRedRice1Kg1800x1000.jpg',
    'Organic Black Rice': 'https://i.ebayimg.com/images/g/6fsAAOSw3ZVjVWpJ/s-l1200.jpg',
    'Organic Quinoa': 'https://etara-online.com/photos/shares/2022/test/20/G08-quinoa-grain-main.jpg',
    'Organic Foxtail Millet': 'https://www.smartfood.org/wp-content/uploads/2020/10/foxtail-husk-off-1-930x1024.png',
    'Organic Finger Millet': 'https://img.etimg.com/thumb/msid-128813492%2Cwidth-640%2Cheight-480%2Cimgsize-84604%2Cresizemode-4/finger-millet-ragi-the-iron-dense-grain.jpg',
    'Organic Pearl Millet': 'https://media.post.rvohealth.io/wp-content/uploads/2020/10/bajra-pearl-millet-grain-732x549-thumbnail-732x549.jpg',
    'Organic Little Millet': 'https://bazaar5.com/image/cache/catalog/pro/product/apiData/b00pagno98-24-mantra-little-millet-500gms-pack-of-1-100-organic-chemical-free-pesticides-free-gluten-free--0-2000x2000.jpg',
    'Organic Kodo Millet': 'https://cdn.shopify.com/s/files/1/2598/1404/files/Buykodomilletonline-img.webp',
    'Organic Barnyard Millet': 'https://cpimg.tistatic.com/10951881/b/4/barnyard-millet.jpg',
    'Organic Green Moong Dal': 'https://tiimg.tistatic.com/fp/1/007/562/100-percent-fresh-natural-chemical-pesticide-free-unpolished-green-moong-daal--635.jpg',
    'Organic Black Urad Dal': 'https://www.jiomart.com/images/product/600x600/rv7w6fhi8z/soni-farms-organic-unpolished-kali-urad-dal-sabut-urad-black-whole-2-kg-product-images-orv7w6fhi8z-p593790207-0-202209152122.jpg',
    'Organic Chana Dal': 'https://www.jiomart.com/images/product/original/490024261/rajdhani-chana-dal-2-kg-product-images-o490024261-p590882244-0-202506201725.jpg?im=Resize%3D%281000%2C1000%29',
    'Organic Masoor Dal': 'https://www.starquik.com/cdn/shop/files/SQ111809_FOP_910ec918-3d59-497e-8ed3-733314a5080a.jpg?v=1775027193&width=533',
    'Organic Kabuli Chana': 'https://img06.weeecdn.com/product/image/597/893/40FF56298584F3B4.jpeg',
    'Organic Rajma': 'https://upload.wikimedia.org/wikipedia/commons/d/d1/Rajma.jpg',
    'Organic Black Chana': 'https://ikaiorganic.com/cdn/shop/files/Gemini_Generated_Image_r4n8wmr4n8wmr4n8.png?v=1782288840',
    'Organic Green Gram': 'https://i.ebayimg.com/images/g/hGMAAOSwr1hmblMG/s-l500.jpg',
    'Organic Red Kidney Beans': 'https://lifegid.com/media/res/1/3/9/2/1/13921.p060y0.600.jpg',
    'Organic Barley': 'https://wholefoodsbox.co.uk/cdn/shop/files/jn188.jpg?v=1719084630',
    'Organic Rolled Oats': 'https://vavapantry.com.au/cdn/shop/products/kialla-rolled-oats-organic-australia_1092c8e4-14be-4b97-a84a-7b9f46ec9fb9_1400x.png?v=1593592943',
    'Organic Broken Wheat': 'https://puretreefoods.com/cdn/shop/files/PT0084-000400BP.MAIN.jpg?v=1750417054',
    'Organic Turmeric Powder': 'https://images.unsplash.com/photo-1615485500704-8e990f9900f7?auto=format&fit=crop&w=900&q=85',
    'Organic Black Pepper': 'https://upload.wikimedia.org/wikipedia/commons/8/84/Black_pepper.jpg',
    'Organic Cumin Seeds': 'https://thamesorganic.com/cdn/shop/files/Organic_Cumin_Seeds_100_gr_1200x1200.jpg?v=1768397343',
    'Organic Coriander Powder': 'https://i5.walmartimages.com/seo/USDA-Organic-Coriander-Powder-4-oz-Spice-Profile-Freshly-Ground-Dhaniya-Cilantro-Molido-Lab-Tested-for-Purity_275315f5-e589-4126-b3e2-bda5f4b81bc1.9950123d7121617ed3db767e9a287d20.jpeg',
    'Organic Red Chilli Powder': 'https://melionsbrothers.com/cdn/shop/files/61wxx_CyZrL._SL1080_bb5524fa-a337-4489-b794-fa8ba0ad7d22.jpg?v=1745933839&width=3840',
    'Organic Green Cardamom': 'https://onsullivan.com/cdn/shop/products/76.jpg?v=1571770395',
    'Organic Cloves': 'https://i5.walmartimages.com/seo/SPICY-ORGANIC-Cloves-Whole-ESF27-100-Pure-USDA-Organic-Non-GMO-Keto-Friendly-Non-Irradiated-Fresh-Clove-Seed-Spice-4-OZ_4d385cbc-3877-47bd-a6c3-81c97ad4cea8.4e65b038b5533e241f3b14a5c53bd167.jpeg',
    'Organic Cinnamon': 'https://down-my.img.susercontent.com/file/my-11134207-7r992-lv1jysjjq6go47',
    'Organic Fennel Seeds': 'https://thamesorganic.com/cdn/shop/files/Organic_Fennel_Seeds_250g_1078x1078.jpg?v=1779324290',
    'Organic Fenugreek Seeds': 'https://www.jiomart.com/images/product/original/rvpmwkxpjv/24-mantra-organic-fenugreek-seeds-methi-dana-menthi-ginja-100gms-pack-of-1-100-organic-chemical-free-pesticides-free-product-images-orvpmwkxpjv-p606766671-0-202312162047.jpg?im=Resize%3D%281000%2C1000%29',
    'Organic Mustard Seeds': 'https://upload.wikimedia.org/wikipedia/commons/4/4d/Mustard_seeds.JPG',
    'Organic Ajwain': 'https://upload.wikimedia.org/wikipedia/commons/0/0e/Ajwain.JPG',
    'Organic Bay Leaves': 'https://commons.wikimedia.org/wiki/Special:Redirect/file/Bay_leaves.jpg',
    'Organic Star Anise': 'https://commons.wikimedia.org/wiki/Special:Redirect/file/Star_anise.jpg',
    'Organic Nutmeg': 'https://cdn.notonthehighstreet.com/fs/c3/24/316f-b54e-484e-bc80-fa3ee5d59fee/original_organic-whole-nutmeg-100g-for-cooking.jpg',
    'Organic Mace': 'https://upload.wikimedia.org/wikipedia/commons/9/90/Nutmeg_mace.JPG',
    'Organic Dry Ginger': 'https://5.imimg.com/data5/SELLER/Default/2024/2/389940198/WU/MB/KB/66789684/organic-adrak-500x500.jpg',
    'Organic Asafoetida': 'https://www.lakshmiayurveda.com.au/cdn/shop/files/IMG_8725.jpg?v=1757337280&width=1200',
    'Organic Garam Masala': 'https://commons.wikimedia.org/wiki/Special:Redirect/file/Garam_Masala.JPG',
    'Organic Sambar Powder': 'https://www.gosupps.com/media/catalog/product/cache/25/small_image/1500x1650/9df78eab33525d08d6e5fb8d27136e95/8/1/81nM6FnLDUL_2.jpg',
    'Organic Rasam Powder': 'https://commons.wikimedia.org/wiki/Special:Redirect/file/Rasam_powder_picture.JPG',
    'Organic Curry Powder': 'https://commons.wikimedia.org/wiki/Special:Redirect/file/Curry_powder.jpg',
    'Organic Chaat Masala': 'https://commons.wikimedia.org/wiki/Special:Redirect/file/Chaatmasala.jpg',
    'Organic Kashmiri Chilli Powder': 'https://upload.wikimedia.org/wikipedia/commons/4/4f/Kashmiri_Red_Chilies.jpg',
    'Organic Panch Phoron': 'https://commons.wikimedia.org/wiki/Special:Redirect/file/Panch-phoron.jpg',
    'Roasted Makhana (Fox Nuts)': 'https://healthymaster.in/cdn/shop/articles/recipe_for_makhana_chaat.jpg?v=1691743824',
    'Mixed Dry Fruit Trail Mix': 'https://www.silkrute.com/images/detailed/1951/51YteLqU0yL_kvfs-t2.jpg',
    'Organic Almonds': 'https://cdn11.bigcommerce.com/s-dis4vxtxtc/images/stencil/608x608/products/2016/5582/Organic-Almonds-1kg-Side-NUALM2.1.2__47624.1665528455.jpg?c=2',
    'Organic Cashews': 'https://m.media-amazon.com/images/I/51sGFb%2BDSML._SL1000_.jpg',
    'Organic Walnuts': 'https://cdn0.woolworths.media/content/wowproductimages/large/133476_1.jpg',
    'Organic Raisins': 'https://cdn11.bigcommerce.com/s-dis4vxtxtc/images/stencil/1280x1280/products/4941/9256/Organic-Raisins-200g-Front-DRRAI2.200__98285.1710740212.jpg?c=2%3Fimbypass%3Don',
    'Organic Dates': 'https://i5.walmartimages.com/seo/Organic-California-Medjool-Dates-8-Ounces-Non-GMO-Whole-Dry-Fancy-Dates-with-Pits_c2510768-88cf-4389-8f89-4aad0967211c.dd7ddf3d21d054d4022668b272f22d94.jpeg?odnBg=FFFFFF&odnHeight=580&odnWidth=580',
    'Organic Pistachios': 'https://cdn.shopaccino.com/rootzorganics/products/pistachios-5784084079764246_m.jpg?v=569',
    'Roasted Chickpeas': 'https://commons.wikimedia.org/wiki/Special:Redirect/file/Roasted_chickpeas.jpg',
    'Organic Peanut Chikki': 'https://snapcalorie-webflow-website.s3.us-east-2.amazonaws.com/media/food_pics_v2/medium/peanut_chikki.jpg',
    'Organic Sesame Chikki': 'https://images.indianexpress.com/2019/01/til-chikki.jpg',
    'Organic Jowar Puffs': 'https://thecowboysfarm.com/cdn/shop/files/CLASSIC_JOWAR_PUFF.jpg?v=1761809674&width=1445',
    'Organic Ragi Chips': 'https://www.snaxup.com/cdn/shop/files/692513a.jpg?v=1758874718&width=1500',
    'Organic Banana Chips': 'https://naturalhealthorganics.com.au/cdn/shop/products/lotus-organic-banana-chips-150g.jpg?v=1617943615',
    'Organic Jackfruit Chips': 'https://archipelago-store.com/cdn/shop/files/Screenshot_2024-10-11_at_1.04.57_PM.png?v=1733347084',
    'Organic Sweet Potato Chips': 'https://balevbiomarket.com/storage/26913/conversions/product_main_image_202708-thumb-620x620.webp',
    'Organic Millet Cookies': 'https://www.bbassets.com/media/uploads/p/l/40301716_1-gudmom-gluten-free-millet-cookies-100-natural-jaggery.jpg',
    'Organic Oat Cookies': 'https://www.organics.ph/cdn/shop/files/gullon-bio-organic-cookies-oats-250g-snacks-landers-superstore-sr-membership-shopping-979440_1024x.jpg?v=1748520607',
    'Organic Coconut Cookies': 'https://cdn.naturamarket.ca/catalog/product/cache/3c698a5d7124ca2538b36bdae68c5d8c/e/m/emmys-organics-coconut-vanilla-min.jpg',
    'Organic Granola': 'https://commons.wikimedia.org/wiki/Special:Redirect/file/1_Granola.jpg',
    'Organic Trail Mix': 'https://assets.woolworths.com.au/images/1005/763844.jpg?impolicy=wowbumxfyzp',
    'Roasted Pumpkin Seeds': 'https://cupofyum.com/uploads/images/000/195/183/195183-roasted-pumpkin-seeds-perfectly-crispy-e64d628fc56cdddc85b8df745dfe8125.jpg',
    'Roasted Sunflower Seeds': 'https://www.zifiti.com/images/itemImgOrig/106/106_2357966.jpg',
    'Organic Coconut Chips': 'https://thamesorganic.com/cdn/shop/files/Coconut_Chips_100g_1024x1024.jpg?v=1768465997',
    'Organic Murukku': 'https://cdn.dotpe.in/longtail/store-items/6368205/UcYItuTz.webp',
    'Raw Forest Honey': 'https://www.bbassets.com/media/uploads/p/xl/40129245_9-natures-nectar-select-honey-forest.jpg',
    'Organic Jaggery': 'https://www.bbassets.com/media/uploads/p/l/279802_8-24-mantra-organic-jaggery.jpg',
    'Organic Jaggery Powder': 'https://pureandsure.in/cdn/shop/files/Jaggery-Powder-F_1200x1200.jpg?v=1762237438',
    'Raw Multifloral Honey': 'https://triphal.com/cdn/shop/files/Raw-Honey-by-Triphal---Pure-Best-Quality-Shahad---1.jpg?crop=center&height=800&v=1779103576&width=800',
    'Organic Wildflower Honey': 'https://www.realfoods.co.uk/ProductImagesID/44009_1.jpg',
    'Organic Acacia Honey': 'https://commons.wikimedia.org/wiki/Special:Redirect/file/Honey_1.jpg',
    'Organic Neem Honey': 'https://pureindiankitchen.com/cdn/shop/files/pure_indian_kitchen_neem_honey.png?v=1770217355&width=416',
    'Organic Jamun Honey': 'https://mirchi.com/os/cdn/content/images/jamun%20honey%20shivaa%20organic_medium_0492448.webp',
    'Organic Date Syrup': 'https://datules.lt/wp-content/uploads/2024/08/Frontal-Verpackung-scaled.jpg',
    'Organic Coconut Sugar': 'https://d2lnr5mha7bycj.cloudfront.net/product-image/file/large_37ad13c1-8f6f-4091-9196-b04799c35008.png',
    'Organic Palm Jaggery': 'https://commons.wikimedia.org/wiki/Special:Redirect/file/Organic_palm_jaggery.jpg',
    'Organic Cane Sugar': 'https://m.media-amazon.com/images/I/51xXYjecAaL._FMwebp__SR600%2C600_.jpg',
    'Organic Stevia Powder': 'https://www.novanutritions.com/cdn/shop/products/Banner3_83a3bc28-58c4-441d-91e1-32a2665b79b0_600x600.jpg?v=1681757035',
    'Organic Maple Syrup': 'https://commons.wikimedia.org/wiki/Special:Redirect/file/Maple_syrup.jpg',
    'Organic Agave Syrup': 'https://commons.wikimedia.org/wiki/Special:Redirect/file/Agave_syrup.jpg',
    'Organic Aloe Vera Gel': 'https://commons.wikimedia.org/wiki/Special:Redirect/file/Aloe_vera_gel_%2820241107%29.jpg',
    'Herbal Neem Soap': 'https://cdn11.bigcommerce.com/s-kg2w7z8739/products/28802/images/81167/M-S814__66846.1731699001.386.513.jpg?c=1',
    'Organic Turmeric Soap': 'https://pareero.com/cdn/shop/files/turmeric-organic-soap.jpg',
    'Organic Sandalwood Soap': 'https://www.rootsandmuds.com/cdn/shop/files/6298044190526_3.jpg?v=1754680303&width=533',
    'Organic Coconut Soap': 'https://phutawan.jp/cdn/shop/files/2112200002221-01.jpg?v=1770865824',
    'Organic Rose Face Wash': 'https://hnmnaturals.com/cdn/shop/files/rose-face-wash-75ml.jpg',
    'Organic Neem Face Wash': 'https://www.jiomart.com/images/product/original/rvq8ugrsex/khadi-organique-face-care-combo-rose-water-toner-neem-face-wash-pack-of-2-420-ml-product-images-orvq8ugrsex-p594285586-4-202210060813.jpg?im=Resize%3D%28420%2C420%29',
    'Organic Aloe Face Wash': 'https://organicbeauty.pk/cdn/shop/files/Aloe_Vera_Face_Wash.jpg?v=1748937955',
    'Organic Coconut Shampoo': 'https://www.beauty.store.bg/dcrimg/277599/bio-shampoan-s-bio-kokosovo-maslo-planeta-organica.jpg',
    'Organic Hibiscus Shampoo': 'https://aorganicstore.com/cdn/shop/files/hibiscus-shampoo-pack.png?v=1771442260',
    'Organic Amla Hair Oil': 'https://khadiorganique.com/cdn/shop/files/Amla02_fefb8c66-cd47-41a9-ad0a-e54ecfa489b7.jpg?v=1735208436',
    'Organic Coconut Hair Oil': 'https://commons.wikimedia.org/wiki/Special:Redirect/file/Baroy_Lanao_Hair_conditioner_serum_Jasminum_essential_virgin_coconut_oil_rear2.jpg',
    'Organic Rose Water': 'https://www.suneetalondon.co.uk/cdn/shop/products/rosewater500ml.jpg?v=1648579971&width=1445',
    'Organic Neem Powder': 'https://hennahubstore.com/cdn/shop/files/10_3_940x.jpg?v=1743674606',
    'Organic Multani Mitti': 'https://organicmandyatest.myshopify.com/cdn/shop/files/Multani-Mitti-Front-100g.jpg',
}

# ============================================================================
# CATEGORY IMAGES FOR FRONTEND
# ============================================================================
# These are intentionally separate from product image_url values.
# The current Category model shown in this project does not have an image_url
# column, so this mapping is safe to import/use from the frontend integration
# layer. If you add Category.image_url later, seed_categories() can persist it.
CATEGORY_IMAGES = {'Fruits': 'https://images.unsplash.com/photo-1610832958506-aa56368176cf?auto=format&fit=crop&w=1200&q=85', 'Vegetables': 'https://images.unsplash.com/photo-1540420773420-3366772f4999?auto=format&fit=crop&w=1200&q=85', 'Organic Oils': 'https://images.unsplash.com/photo-1474979266404-7eaacbcd87c5?auto=format&fit=crop&w=1200&q=85', 'Juices & Beverages': 'https://images.unsplash.com/photo-1600271886742-f049cd451bba?auto=format&fit=crop&w=1200&q=85', 'Grains & Pulses': 'https://images.unsplash.com/photo-1586201375761-83865001e31c?auto=format&fit=crop&w=1200&q=85', 'Spices': 'https://images.unsplash.com/photo-1596040033229-a9821ebd058d?auto=format&fit=crop&w=1200&q=85', 'Snacks': 'https://images.unsplash.com/photo-1621939514649-280e2aa8ad25?auto=format&fit=crop&w=1200&q=85', 'Honey & Sweeteners': 'https://images.unsplash.com/photo-1587049352846-4a222e784d38?auto=format&fit=crop&w=1200&q=85', 'Personal Care': 'https://images.unsplash.com/photo-1556229010-6c3f2c9ca5f8?auto=format&fit=crop&w=1200&q=85'}

# ============================================================================
# GET PRODUCT IMAGE
# ============================================================================

def get_category_image(category_name: str) -> str | None:
    """Return the frontend category image for a category name."""
    return CATEGORY_IMAGES.get(category_name)


def get_product_image(product_name: str, category_name: str) -> str:
    """Return the required seed image for this exact product name."""
    image_url = PRODUCT_IMAGES.get(product_name)
    if not image_url:
        raise ValueError(
            f"No seed image URL configured for product: {product_name!r} "
            f"(category: {category_name!r})"
        )
    return image_url


# ============================================================================
# SEED CATEGORIES
# ============================================================================

def seed_categories(db):

    category_map = {}

    for name, description in CATEGORIES:

        category = db.scalar(
            select(Category).where(
                Category.name == name
            )
        )

        if category is None:

            category = Category(
                name=name,
                description=description,
                image_url=CATEGORY_IMAGES.get(name),
                is_active=True,
            )

            db.add(category)

            db.flush()

            print(
                f"Created category: {name}"
            )

        else:

            category.description = description
            category.image_url = CATEGORY_IMAGES.get(name)
            category.is_active = True

            print(
                f"Category already exists: {name}"
            )

        category_map[name] = category

    return category_map


# ============================================================================
# SEED PRODUCTS
# ============================================================================

def seed_products(db, category_map):

    created = 0
    updated = 0
    image_count = 0
    missing_images = []

    for (
        name,
        category_name,
        price,
        stock_quantity,
        unit,
        organic,
        vendor,
    ) in PRODUCTS:

        # --------------------------------------------------------------------
        # Validate category
        # --------------------------------------------------------------------

        if category_name not in category_map:

            raise ValueError(
                f"Unknown category '{category_name}' "
                f"for product '{name}'"
            )

        category = category_map[category_name]

        # --------------------------------------------------------------------
        # Check existing product
        # --------------------------------------------------------------------

        product = db.scalar(
            select(Product).where(
                Product.seller_id == DEMO_FARMER_ID,
                Product.name == name,
            )
        )

        # --------------------------------------------------------------------
        # Always use the deterministic seed mapping.
        # This repairs stale, broken, or previously-null DB image URLs.
        # --------------------------------------------------------------------
        image_url = get_product_image(
            product_name=name,
            category_name=category_name,
        )

        # --------------------------------------------------------------------
        # Image status
        # --------------------------------------------------------------------

        if image_url:

            image_count += 1

            print(
                f"Image assigned: {name}"
            )

        else:

            missing_images.append(name)

            print(
                f"WARNING: No image found: {name}"
            )

        # --------------------------------------------------------------------
        # Product description
        # --------------------------------------------------------------------

        description = (
            f"{'Organic' if organic else 'Natural'} "
            f"{name}."
        )

        # --------------------------------------------------------------------
        # CREATE
        # --------------------------------------------------------------------

        if product is None:

            product = Product(
                seller_id=DEMO_FARMER_ID,
                category_id=category.id,
                name=name,
                description=description,
                price=Decimal(str(price)),
                stock_quantity=stock_quantity,
                unit=unit,
                certification="APPROVED",
                image_url=image_url,
                is_active=True,
            )

            db.add(product)

            created += 1

            print(
                f"Created product: {name}"
            )

        # --------------------------------------------------------------------
        # UPDATE
        # --------------------------------------------------------------------

        else:

            product.category_id = category.id
            product.description = description
            product.price = Decimal(str(price))
            product.stock_quantity = stock_quantity
            product.unit = unit
            product.certification = "APPROVED"
            product.is_active = True

            # Always replace the image with the validated seed URL.
            product.image_url = image_url

            updated += 1

            print(
                f"Updated product: {name}"
            )

    return (
        created,
        updated,
        image_count,
        missing_images,
    )


# ============================================================================
# VALIDATION
# ============================================================================

def validate_catalog():

    product_count = len(PRODUCTS)

    category_count = len(CATEGORIES)

    print()
    print("=" * 70)
    print("CATALOG VALIDATION")
    print("=" * 70)

    print(
        f"Categories defined : {category_count}"
    )

    print(
        f"Products defined   : {product_count}"
    )

    if category_count != 9:

        raise ValueError(
            f"Expected 9 categories, "
            f"found {category_count}"
        )

    if product_count != 200:

        raise ValueError(
            f"Expected exactly 200 products, "
            f"found {product_count}"
        )

    # ------------------------------------------------------------------------
    # Validate product categories
    # ------------------------------------------------------------------------

    valid_categories = {
        name for name, _ in CATEGORIES
    }

    invalid_products = [
        (
            name,
            category_name,
        )
        for (
            name,
            category_name,
            price,
            stock,
            unit,
            organic,
            vendor,
        ) in PRODUCTS
        if category_name not in valid_categories
    ]

    if invalid_products:

        print("\nInvalid products:")

        for name, category_name in invalid_products:

            print(
                f"  {name} -> {category_name}"
            )

        raise ValueError(
            "One or more products contain "
            "invalid categories."
        )

    # ------------------------------------------------------------------------
    # Check duplicate product names
    # ------------------------------------------------------------------------

    names = [
        product[0]
        for product in PRODUCTS
    ]

    duplicates = {
        name
        for name in names
        if names.count(name) > 1
    }

    if duplicates:

        raise ValueError(
            "Duplicate product names found: "
            + ", ".join(sorted(duplicates))
        )

    print()
    print("Catalog validation passed.")
    print("=" * 70)


# ============================================================================
# IMAGE VALIDATION
# ============================================================================

def validate_product_images():
    """Require exactly one non-empty HTTP(S) image URL for every product."""
    product_names = {product[0] for product in PRODUCTS}
    mapped_names = set(PRODUCT_IMAGES)

    if mapped_names != product_names:
        missing = sorted(product_names - mapped_names)
        extra = sorted(mapped_names - product_names)
        raise ValueError(
            f"Image mapping mismatch. Missing: {missing}; Extra: {extra}"
        )

    missing_or_blank = [
        name for name, url in PRODUCT_IMAGES.items()
        if not isinstance(url, str) or not url.strip()
    ]
    if missing_or_blank:
        raise ValueError(
            "Products with missing/blank image URLs: "
            + ", ".join(sorted(missing_or_blank))
        )

    invalid_urls = [
        (name, url)
        for name, url in PRODUCT_IMAGES.items()
        if not url.startswith(("http://", "https://"))
    ]
    if invalid_urls:
        raise ValueError(
            "Invalid image URLs:\n"
            + "\n".join(f"  {name}: {url}" for name, url in invalid_urls)
        )

    urls = list(PRODUCT_IMAGES.values())
    duplicates = {url for url in urls if urls.count(url) > 1}
    if duplicates:
        raise ValueError(
            "Duplicate product image URLs detected:\n"
            + "\n".join(sorted(duplicates))
        )

    print(f"Image mappings defined : {len(PRODUCT_IMAGES)}")
    print(f"Unique seed image URLs : {len(urls)}")
    print(f"Products with no image : 0")
    print("Image mapping validation passed.")


# ============================================================================
# MAIN
# ============================================================================

def main():

    print("=" * 70)
    print("OrganicKart Product Catalog Seed")
    print("=" * 70)

    # ------------------------------------------------------------------------
    # Validate the hardcoded catalog BEFORE touching the database.
    # ------------------------------------------------------------------------

    validate_catalog()
    validate_product_images()

    # ------------------------------------------------------------------------
    # Database session
    # ------------------------------------------------------------------------

    db = SessionLocal()

    try:

        # --------------------------------------------------------------------
        # Categories
        # --------------------------------------------------------------------

        print()
        print("Seeding categories...")

        category_map = seed_categories(db)

        # --------------------------------------------------------------------
        # Products
        # --------------------------------------------------------------------

        print()
        print("Seeding products...")

        (
            created,
            updated,
            image_count,
            missing_images,
        ) = seed_products(
            db,
            category_map,
        )

        # --------------------------------------------------------------------
        # Commit
        # --------------------------------------------------------------------

        db.commit()

        # --------------------------------------------------------------------
        # Summary
        # --------------------------------------------------------------------

        print()
        print("=" * 70)
        print("SEED COMPLETE")
        print("=" * 70)

        print(
            f"Categories          : {len(category_map)}"
        )

        print(
            f"Products defined    : {len(PRODUCTS)}"
        )

        print(
            f"Products created    : {created}"
        )

        print(
            f"Products updated    : {updated}"
        )

        print(
            f"Images assigned     : {image_count}"
        )

        print(
            f"Images missing      : {len(missing_images)}"
        )

        print(
            f"Seller ID           : {DEMO_FARMER_ID}"
        )

        # --------------------------------------------------------------------
        # Missing images
        # --------------------------------------------------------------------

        if missing_images:

            print()
            print("Products without images:")

            for product_name in missing_images:

                print(
                    f"  - {product_name}"
                )

        else:

            print()
            print(
                "SUCCESS: Seed image URLs are unique; products without images are ready for vendor upload."
            )

        print("=" * 70)

    except Exception:

        db.rollback()

        raise

    finally:

        db.close()


# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    main()
