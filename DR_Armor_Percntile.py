# Program to figure out % of an item based off rarity, level, tier, and health of a piece of armor
# This based off the item at its drop, does not account for the "rounding" from orbs of wisdom 
from fractions import Fraction

# Had to make dictionary elements, this is the cleanest way to do it because they are hard-coded numbers

# T1 ranges by 5 for each rarity
best_t1 = {
    "common": 18,
    "uncommon": 26,
    "rare": 34,
    "epic": 42,
    "legendary": 50
}

# T2 ranges by 13 for each rarity
best_t2 = {
    "common": 78,
    "uncommon": 96,
    "rare": 114,
    "epic": 132,
    "legendary": 150
}

# T3 ranges by 37 for each rarity
best_t3 = {
    "common": 234,
    "uncommon": 288,
    "rare": 342,
    "epic": 396,
    "legendary": 450
}

# T4 ranges by 109 for each rarity
best_t4 = {
    "common": 702,
    "uncommon": 864,
    "rare": 1026,
    "epic": 1188,
    "legendary": 1350
}

# T5 ranges by 325 for each rarity
best_t5 = {
    "common": 2106,
    "uncommon": 2592,
    "rare": 3078,
    "epic": 3564,
    "legendary": 4050
}

# tier 1 min common is 14hp at level 1 unplussed 
# tier 2 min common is 66hp at level 21 unplussed 
# tier 3 min common is 198hp at level 41 unplussed 
# tier 4 min common is 594hp at level 61 unplussed
# tier 5 min common is 1782hp at level 81 unplussed

# tier 1 max legendary is 75hp at level 20 unplussed ~ 91hp +4
# tier 2 max legendary is 225hp at level 40 unplussed ~ 273hp +4
# tier 3 max legendary is 675hp at level 60 unplussed ~ 820hp +4
# tier 4 max legendary is 2,025hp at level 80 unplussed ~ 2,461hp +4
# tier 5 max legendary is 6,075hp at level 100 unplussed ~ 7,384hp +4

# In order to find lowest level hp use multiplicative inverse, then reciprocal
# numpy doesn't want to import properly so had to do reciprocal manually
def original_hp(level, health, tier):
    base_hp = Fraction((((level - ((tier-1) * 20)) / 20) / 2) + 1)
    base_hp = str(base_hp).split("/")
    base_hp[0], base_hp[1] = (base_hp[1], base_hp[0])
    base_hp = (int(base_hp[0]) / int(base_hp[1]))
    return base_hp * health
                
if __name__ == "__main__":
    print(f"Follow prompts to find percentile of item. 50th percentile means that the item is average for its rarity. Higher is better, lower is worse.")
    while True:
        tier = int(input("Enter Tier of Item (Ex: 3): "))
        if tier >= 1 and tier <= 5:
            break
        print("Invalid Tier")
    
    while True:
        level = int(input("Enter Level of Item (Ex: 56): "))
        if level <= (tier * 20) and level > ((tier-1) * 20):
            break
        print("Invalid Level for tier")

    while True:
        rarity = input("Enter Rarity of Item (Ex: Rare): ").lower()
        if rarity == "common" or rarity == "uncommon" or rarity == "rare" or rarity == "epic" or rarity == "legendary":
            break
        print("Invalid Rarity")   

    health = float(input("Enter Health of Item (Ex: 331): "))

    original = (original_hp(level,health,tier))

    # To get the percentile, reference the dictionary via tier then get percentile by dividing original by corresponding tier and max hp

    match tier:
        case 1:
            percentage = ((1 - ((float(best_t1[rarity]) - original) / 5))*100)
            if percentage > 100 or percentage < 0:
                print("Percentile out of range, this means user entered invalid health number for corresponding elements")
            print(f"{percentage:.2f} Percentile for Tier {tier} {rarity.title()}")
        case 2:
            percentage = ((1 - ((float(best_t2[rarity]) - original) / 13))*100)
            if percentage > 100 or percentage < 0:
                print("Percentile out of range, this means user entered invalid health number for corresponding elements")
            print(f"{percentage:.2f} Percentile for Tier {tier} {rarity.title()}")
        case 3:
            percentage = ((1 - ((float(best_t3[rarity]) - original) / 37))*100)
            if percentage > 100 or percentage < 0:
                print("Percentile out of range, this means user entered invalid health number for corresponding elements")
            print(f"{percentage:.2f} Percentile for Tier {tier} {rarity.title()}")
        case 4:
            percentage = ((1 - ((float(best_t4[rarity]) - original) / 109))*100)
            if percentage > 100 or percentage < 0:
                print("Percentile out of range, this means user entered invalid health number for corresponding elements")
            print(f"{percentage:.2f} Percentile for Tier {tier} {rarity.title()}")
        case 5:
            percentage = ((1 - ((float(best_t5[rarity]) - original) / 325))*100)
            if percentage > 100 or percentage < 0:
                print("Percentile out of range, this means user entered invalid health number for corresponding elements")
            print(f"{percentage:.2f} Percentile for Tier {tier} {rarity.title()}")
        case _:
            print("Unknown")