# %%
import json

with open("validated_summaries.json", "r") as file:
    data = json.load(file)

# Count the number of letter_name keys
count = len(data)

# Print the count
print(f"The number of letter_name keys is: {count}")
# %%
