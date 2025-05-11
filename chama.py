#The company has some event data come as JSONs, and it needs some transformations to be structured as tables. Convert the presented case.json file to three CSV files, with the following rules:

#Introduction and Data Exploration
import pandas as pd

df = pd.read_json(path_or_buf="case.json")
df.sample(n=10, random_state=42)
df.shape
df.head()
# transform to Brazilian timezone
df["EnqueuedTimeUtc"] = pd.to_datetime(arg=df["EnqueuedTimeUtc"]).dt.tz_convert(tz="Brazil/East")
df.head()
print(df["EventName"].value_counts())

#DynamicPriceOption

dynamic_price_events = df[df["EventName"] == "DynamicPrice_Result"]
dynamic_price_events.shape

dynamic_price_events.head()

import json


def dynamic_price_option(row):
    """Transform the JSON payload into a dynamic price option dataframe."""
    enqueued_time = row["EnqueuedTimeUtc"].to_pydatetime().strftime("%d/%m/%y")
    payload_row = row["Payload"]
    payload_row = json.loads(payload_row)
    result = []
    if payload_row["provider"] == "ApplyDynamicPricePerOption":
        provider = f"\"{payload_row['provider']}\""
        offer_id = f"\"{payload_row['offerId']}\""
        for unique_option in payload_row["algorithmOutput"]:
            price_option = {
                "Provider": provider,
                "OfferId": offer_id,
                "UniqueOptionId": f"\"{unique_option['uniqueOptionId']}\"",
                "BestPrice": unique_option["bestPrice"],
                "EnqueuedTimeSP": enqueued_time
            }
            result.append(price_option)
    return result


lst = dynamic_price_events.apply(dynamic_price_option, axis=1)
flatten = [x for xs in lst for x in xs]
dynamic_price_option_payload = pd.DataFrame(flatten)

dynamic_price_option_payload

dynamic_price_option_payload.to_csv("dynamic_price_option_payload.csv", index=False)

#DynamicPriceRange

def dynamic_price_range(row):
    """Transform the JSON payload into a dynamic price range dataframe."""
    enqueued_time = row["EnqueuedTimeUtc"].to_pydatetime().strftime("%d/%m/%y")
    payload_row = row["Payload"]
    payload_row = json.loads(payload_row)
    result = []
    if payload_row["provider"] == "ApplyDynamicPriceRange":
        provider = f"\"{payload_row['provider']}\""
        offer_id = f"\"{payload_row['offerId']}\""
        algorithm_output = payload_row["algorithmOutput"]
        price_range = {
            "Provider": provider,
            "OfferId": offer_id,
            "MinGlobal": algorithm_output["min_global"],
            "MinRecommended": algorithm_output["min_recommended"],
            "MaxRecommended": algorithm_output["max_recommended"],
            "DifferenceMinRecommendMinTheory": algorithm_output["differenceMinRecommendMinTheory"],
            "EnqueuedTimeSP": enqueued_time
        }
        result.append(price_range)
    return result


lst = dynamic_price_events.apply(dynamic_price_range, axis=1)
flatten = [x for xs in lst for x in xs]
dynamic_price_range_payload = pd.DataFrame(flatten)

dynamic_price_range_payload
dynamic_price_range_payload.to_csv("dynamic_price_range_payload.csv", index=False)

#CurratedOfferOptions
curated_offers = df[df["EventName"] == "CurateOffer_Result"]
curated_offers.shape
curated_offers.head()

def curated_offer(row):
    """Transform JSON payload into curated offer dataframe."""
    enqueued_time = row["EnqueuedTimeUtc"].to_pydatetime().strftime("%d/%m/%y")
    payload_row = row["Payload"]
    payload_row = json.loads(payload_row)
    result = []
    for el in payload_row:
        curation_provider = f"\"{el['curationProvider']}\""
        offer_id = f"\"{el['offerId']}\""
        dealer_id = f"\"{el['dealerId']}\""
        for option in el["options"]:
            offer_options = {
                "CurationProvider": curation_provider,
                "OfferId": offer_id,
                "DealerId": dealer_id,
                "UniqueOptionId": f"\"{option['uniqueOptionId']}\"",
                "OptionId": f"\"{option['optionId']}\"",
                "IsMobileDealer": option["isMobileDealer"],
                "IsOpen": option["isOpen"],
                "Eta": f"\"{option['eta']}\"",
                "ChamaScore": option["chamaScore"],
                "ProductBrand": f"\"{option['productBrand']}\"",
                "IsWinner": option["isWinner"],
                "MinimumPrice": option["minimumPrice"],
                "MaximumPrice": option["maximumPrice"],
                "DynamicPrice": option["dynamicPrice"],
                "FinalPrice": option["finalPrice"]
            }
            if "defeatPrimaryReason" in option:
                offer_options["DefeatPrimaryReason"] = f"\"{option['defeatPrimaryReason']}\""
                offer_options["DefeatReasons"] = f"\"{option['defeatReasons']}\""
            else:
                offer_options["DefeatPrimaryReason"] = "\"\""
                offer_options["DefeatReasons"] = "\"\""
            offer_options["EnqueuedTimeSP"] = enqueued_time
            result.append(offer_options)
    return result


flatten = [x for xs in curated_offers.apply(curated_offer, axis=1) for x in xs]
curated_offers_payload = pd.DataFrame(flatten)

curated_offers_payload

curated_offers_payload.to_csv("curated_offers_payload.csv", index=False)