import requests
import pandas as pd
import base64
import time


def get_ebay_access_token(app_id, cert_id):
    print("Verifying and retrieving the token from eBay...")
    # Encode the authentication string in Base64 according to eBay's standard
    auth_string = f"{app_id}:{cert_id}"
    encoded_auth = base64.b64encode(auth_string.encode()).decode('utf-8')
    
    url = 'https://api.ebay.com/identity/v1/oauth2/token'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Authorization': f'Basic {encoded_auth}'
    }
    data = {
        'grant_type': 'client_credentials',
        'scope': 'https://api.ebay.com/oauth/api_scope'
    }
    
    response = requests.post(url, headers=headers, data=data)
    
    if response.status_code == 200:
        print("-> Get Token successfully!")
        return response.json()['access_token']
    else:
        print("-> Authentication error:", response.json())
        return None


def _extract_item_features(item, query):
    shipping_option = item.get('shippingOptions', [{}])[0] if item.get('shippingOptions') else {}
    shipping_cost_obj = shipping_option.get('shippingCost', {})
    availability = item.get('availability', {})
    seller = item.get('seller', {})
    category = item.get('categories', [{}])[0] if item.get('categories') else {}
    item_location = item.get('itemLocation', {})

    price_value = item.get('price', {}).get('value')
    shipping_value = shipping_cost_obj.get('value', 0)

    try:
        total_cost = float(price_value) + float(shipping_value)
    except (TypeError, ValueError):
        total_cost = None

    return {
        'query': query,

        # ID & Link
        'item_id': item.get('itemId'),
        'legacy_item_id': item.get('legacyItemId'),
        'item_web_url': item.get('itemWebUrl'),
        'item_href': item.get('itemHref'),

        # Content 
        'title': item.get('title'),
        'subtitle': item.get('subtitle'),

        # Price and Shipping
        'price': price_value,
        'currency': item.get('price', {}).get('currency'),
        'shipping_cost': shipping_value,
        'shipping_currency': shipping_cost_obj.get('currency'),
        'has_free_shipping': shipping_value in (0, '0', '0.0', '0.00'),
        'total_cost': total_cost,

        # Conditon
        'condition': item.get('condition', 'Unknown'),
        'condition_id': item.get('conditionId'),
        'buying_options': '|'.join(item.get('buyingOptions', [])),
        'top_rated_buying_experience': item.get('topRatedBuyingExperience'),
        'priority_listing': item.get('priorityListing'),
        'adult_only': item.get('adultOnly'),

        # Time 
        'item_creation_date': item.get('itemCreationDate'),
        'item_end_date': item.get('itemEndDate'),

        # Seller
        'seller_username': seller.get('username'),
        'seller_feedback_score': seller.get('feedbackScore'),
        'seller_feedback_percent': seller.get('feedbackPercentage'),

        # Category and location
        'category_id': category.get('categoryId'),
        'category_path': category.get('categoryName'),
        'leaf_category_ids': '|'.join(item.get('leafCategoryIds', [])),
        'item_location_country': item_location.get('country'),
        'item_location_postal': item_location.get('postalCode'),

        # Media
        'image_url': item.get('image', {}).get('imageUrl'),
        'thumbnail_url': item.get('thumbnailImages', [{}])[0].get('imageUrl') if item.get('thumbnailImages') else None,
    }


def scrape_ebay_api_advanced(query, token, target_items=500, pause_seconds=0.5):
    query_items = []
    offset = 0
    limit = 100  
    
    headers = {
        'Authorization': f'Bearer {token}',
        'X-EBAY-C-MARKETPLACE-ID': 'EBAY_US',
        'Accept': 'application/json'
    }
    
    while len(query_items) < target_items:
        print(f"Calling the API to retrieve products from {offset} to {offset + limit}...")
        url = "https://api.ebay.com/buy/browse/v1/item_summary/search"
        params = {
            'q': query,
            'limit': limit,
            'offset': offset,
        }

        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            summaries = data.get('itemSummaries', [])
            
            if not summaries:
                print("All available products have been retrieved.")
                break

            for item in summaries:
                query_items.append(_extract_item_features(item, query))

            offset += limit

            # Stop if we have retrieved all available products according to the API response
            total_available = data.get('total')
            if isinstance(total_available, int) and offset >= total_available:
                print("All available products have been retrieved.")
                break

            time.sleep(pause_seconds)

        else:
            print(f"Error API (Status {response.status_code}): {response.text}")
            break

        if len(query_items) >= target_items:
            break

    df = pd.DataFrame(query_items[:target_items])
    print(f"\n-> Query '{query}' collect {len(df)} products")
    return df


def scrape_ebay_multi_queries(queries, token, target_items_total, pause_seconds=0.5):
    if not queries:
        raise ValueError("Empty queries list.")

    per_query_target = max(1, target_items_total // len(queries))
    print(f"Number of target items per query: {per_query_target}")

    all_frames = []
    for idx, query in enumerate(queries, start=1):
        print(f"\n=== [{idx}/{len(queries)}] Collecting query: '{query}' ===")
        df_query = scrape_ebay_api_advanced(
            query=query,
            token=token,
            target_items=per_query_target,
            pause_seconds=pause_seconds,
        )
        all_frames.append(df_query)

    if not all_frames:
        return pd.DataFrame()

    df_all = pd.concat(all_frames, ignore_index=True)
    before_drop = len(df_all)
    df_all = df_all.drop_duplicates(subset=['item_id'])
    after_drop = len(df_all)

    print(f"\nTotal before removing duplicates: {before_drop}")
    print(f"Total after removing duplicates by item_id: {after_drop}")
    return df_all

APP_ID = "API"
CERT_ID = "API"


PRODUCT_QUERIES = [
    "laptop",
    "smartphone",
    "tablet",
    "camera",
    "headphones",
    "smartwatch",
    "gaming console",
    "monitor",
]

TARGET_ITEMS_TOTAL = 16000

access_token = get_ebay_access_token(APP_ID, CERT_ID)

if access_token:
    df_ebay = scrape_ebay_multi_queries(
        queries=PRODUCT_QUERIES,
        token=access_token,
        target_items_total=TARGET_ITEMS_TOTAL,
        pause_seconds=0.5,
    )

    output_file = "ebay_products.csv"
    df_ebay.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"\nFinished! Saved {len(df_ebay)} products to file: {output_file}")