"""
Curated Mathematical Misconception Taxonomy for Classes 5-7.
Covers 6 foundational skills:
1. Subtraction
2. Addition
3. Multiplication
4. Division
5. Fractions
6. Place Value
"""

TAXONOMY = {
    "Subtraction": {
        "description": "Multi-digit subtraction and regrouping/borrowing concepts.",
        "misconceptions": [
            {
                "id": "SUB_SMALLER_FROM_LARGER",
                "name": "Subtracting smaller digit from larger digit",
                "description": "When the top digit in a column is smaller than the bottom digit, the student subtracts the top digit from the bottom digit instead of borrowing (e.g., 5 - 8 becomes 8 - 5 = 3).",
                "example": "In 35 - 18, calculating 5 - 8 as 8 - 5 = 3, yielding 23 instead of 17.",
                "remediation_strategy": "Rupee-sharing story: 'If you have 5 rupees in your pocket, can you give 8 rupees to your friend? No! You need to borrow a 10-rupee note from the tens pocket.'",
                "default_simple_explanation": "When we subtract 35 - 18, look at the ones column: 5 minus 8. Imagine you have 5 rupees in your pocket. Can you give 8 rupees? No! You cannot take 8 from 5. Instead of turning it around to 8 minus 5, you must borrow 1 ten (10 rupees) from the 30 in the tens place! That makes 15 rupees. Now, 15 minus 8 is 7. And in tens, 20 minus 10 is 10. So 35 minus 18 is 17!"
            },
            {
                "id": "SUB_NO_BORROW_DECREMENT",
                "name": "Forgetting to reduce next place value after borrowing",
                "description": "The student borrows 10 to add to the ones column, but forgets to decrement the digit in the tens column.",
                "example": "In 52 - 27, student does 12 - 7 = 5, but keeps 5 in tens place and does 5 - 2 = 3, getting 35 instead of 25.",
                "remediation_strategy": "Bank teller analogy: 'Once you take 1 ten out of the tens pocket, that pocket has 1 less ten left!'",
                "default_simple_explanation": "Great job regrouping the ones, but remember: when you borrow 1 ten from the tens place, that column decreases by 1! So 5 tens becomes 4 tens. 4 tens minus 2 tens is 2 tens, giving 25."
            },
            {
                "id": "SUB_ZERO_BORROWING",
                "name": "Confusion borrowing across zero",
                "description": "When encountering a zero in intermediate columns, student skips the zero or converts it incorrectly.",
                "example": "In 304 - 158, borrowing directly from hundreds to ones and leaving zero unchanged.",
                "remediation_strategy": "Chain borrowing step-by-step: Hundreds box opens into 10 tens first, then 1 ten opens into 10 ones.",
                "default_simple_explanation": "When borrowing across a zero, remember zero has nothing to give immediately! First borrow from hundreds to make 10 tens, then borrow 1 ten to make 10 ones."
            }
        ]
    },
    "Addition": {
        "description": "Multi-digit addition with carry-over and alignment.",
        "misconceptions": [
            {
                "id": "ADD_FORGET_CARRY",
                "name": "Forgetting carried-over digits",
                "description": "Adding ones column produces a two-digit number, but student ignores or forgets to add the carried ten into the tens column.",
                "example": "In 47 + 38, 7 + 8 = 15 (writes 5), then 4 + 3 = 7, giving 75 instead of 85.",
                "remediation_strategy": "Bundle of sticks analogy: 10 ones bundle up into 1 ten stick that joins the tens pile.",
                "default_simple_explanation": "When you added 7 + 8, you got 15! 15 is 1 ten and 5 ones. The 5 stays in the ones place, but that 1 ten must be carried over and added to 4 + 3! So 1 + 4 + 3 = 8 tens, making 85."
            },
            {
                "id": "ADD_LEFT_TO_RIGHT_NO_REGROUP",
                "name": "Adding multi-digit numbers from left to right without carrying",
                "description": "Adding columns from left to right and concatenating sums without carrying over place values.",
                "example": "In 47 + 38, adding 4 + 3 = 7 and 7 + 8 = 15, writing 715.",
                "remediation_strategy": "Column alignment and right-to-left order explanation using base-10 blocks.",
                "default_simple_explanation": "Always start adding from the right (ones place)! If the sum is 10 or greater, the extra ten moves up to the tens place."
            },
            {
                "id": "ADD_PLACE_MISALIGNMENT",
                "name": "Misaligning place values when numbers have different digit lengths",
                "description": "Aligning numbers by left margin instead of by place value (ones under ones, tens under tens).",
                "example": "Adding 123 + 45 as if 4 is under hundreds and 5 is under tens.",
                "remediation_strategy": "Place value grid: Draw columns labeled H, T, O (Hundreds, Tens, Ones).",
                "default_simple_explanation": "Make sure ones line up under ones and tens line up under tens! 45 has 4 tens and 5 ones, not hundreds."
            }
        ]
    },
    "Multiplication": {
        "description": "Concept of repeated addition, times tables, and multi-digit multiplication.",
        "misconceptions": [
            {
                "id": "MUL_CONFUSE_WITH_ADD",
                "name": "Confusing multiplication with addition",
                "description": "Student adds the numbers together instead of multiplying.",
                "example": "In 6 x 4, answering 10 because 6 + 4 = 10.",
                "remediation_strategy": "Equal groups visual: 'Multiplication means groups! 6 x 4 means 6 groups of 4 chocolates, not just 6 plus 4.'",
                "default_simple_explanation": "Remember, the 'x' sign means groups of! 6 x 4 means having 6 bags, each with 4 chocolates inside. That's 4 + 4 + 4 + 4 + 4 + 4 = 24 chocolates, not 6 + 4."
            },
            {
                "id": "MUL_FORGET_ZERO_PLACEHOLDER",
                "name": "Place-value errors in multi-digit multiplication (forgetting zero place holder)",
                "description": "When multiplying by the tens digit in 2-digit multiplication, student forgets to place a 0 placeholder on the second row.",
                "example": "In 23 x 14, multiplying 23 x 1 and writing 23 directly under 92 instead of shifting it to 230.",
                "remediation_strategy": "Emphasize multiplying by 10, not 1: 'You are multiplying by 1 ten, which is 10, so it must end with a zero!'",
                "default_simple_explanation": "When multiplying by the 1 in 14, remember that 1 is actually in the tens place (it means 10). So we must put a 0 placeholder in the ones column before writing the product!"
            },
            {
                "id": "MUL_TABLE_ERROR",
                "name": "Incorrect multiplication tables",
                "description": "Student understands the operation but miscalculates the basic product due to a table recall mistake.",
                "example": "In 7 x 8, answering 54 instead of 56.",
                "remediation_strategy": "Decomposition trick: 7 x 8 is (7 x 7) + 7 = 49 + 7 = 56.",
                "default_simple_explanation": "Your reasoning is on the right track! For 7 x 8, you can think of 7 x 7 = 49, and add one more 7 to get 56."
            }
        ]
    },
    "Division": {
        "description": "Equal sharing, long division, and remainder handling.",
        "misconceptions": [
            {
                "id": "DIV_REMAINDER_AS_DECIMAL",
                "name": "Confusing remainder with decimal part",
                "description": "Student writes the remainder directly after a decimal point (e.g. 7 ÷ 2 = 3 remainder 1 written as 3.1).",
                "example": "In 13 ÷ 4, writing 3.1 instead of 3.25 or 3 R 1.",
                "remediation_strategy": "Fraction conversion: Remainder 1 over divisor 4 is 1/4 = 0.25, not 0.1.",
                "default_simple_explanation": "A remainder is what is left over to be divided! 1 left over when dividing among 4 friends means each person gets 1/4 more (0.25), not 0.1."
            },
            {
                "id": "DIV_REVERSE_ORDER",
                "name": "Dividing smaller digit by larger digit in long division",
                "description": "Dividing the larger number by the smaller number regardless of dividend/divisor position.",
                "example": "In 3 ÷ 6, answering 2 because 6 ÷ 3 = 2.",
                "remediation_strategy": "Fair share story: 3 rotis shared equally between 6 children means each gets half (1/2 or 0.5) a roti.",
                "default_simple_explanation": "In 3 divided by 6, the 3 is what we have and 6 is how many friends share it! 3 rotis among 6 friends means each gets half a roti (0.5), not 2 rotis."
            },
            {
                "id": "DIV_IGNORE_INTERMEDIATE_ZERO",
                "name": "Ignoring zeros in quotient",
                "description": "Skipping zero when a digit of the dividend cannot be divided by divisor.",
                "example": "In 618 ÷ 6, doing 6 ÷ 6 = 1, skipping 1, and doing 18 ÷ 6 = 3 to get 13 instead of 103.",
                "remediation_strategy": "Every digit gets a turn: If 6 doesn't go into 1, write 0 in the quotient before bringing down the next digit.",
                "default_simple_explanation": "Every digit in long division must have a result! Since 6 goes into 1 zero times, we must write a 0 in the quotient before bringing down the 8. So 618 ÷ 6 is 103, not 13."
            }
        ]
    },
    "Fractions": {
        "description": "Parts of a whole, equivalent fractions, and fraction addition/subtraction.",
        "misconceptions": [
            {
                "id": "FRAC_ADD_DENOMINATORS",
                "name": "Adding denominators directly",
                "description": "Adding both numerators and denominators straight across (e.g., 1/2 + 1/3 = 2/5).",
                "example": "1/4 + 2/4 = 3/8 or 1/2 + 1/3 = 2/5.",
                "remediation_strategy": "Pizza slice analogy: The denominator tells us the size of the slice, not how many slices we have. If you have 1 fourth-slice and 2 fourth-slices, you have 3 fourth-slices (3/4), not 3 eighths!",
                "default_simple_explanation": "Think of a pizza cut into 4 slices. If Aarav eats 1 slice (1/4) and Priya eats 2 slices (2/4), together you ate 3 slices of the 4-slice pizza (3/4)! The size of the slices doesn't change, so we never add denominators!"
            },
            {
                "id": "FRAC_CONFUSE_NUM_DENOM",
                "name": "Confusing numerator and denominator",
                "description": "Mixing up the part (top) with the whole (bottom), reading 3/4 as '4 parts out of 3'.",
                "example": "Interpreting 2/5 as 5 divided into 2 parts.",
                "remediation_strategy": "N for 'Number of parts we have', D for 'Divided total parts' (or 'Down').",
                "default_simple_explanation": "The top number (Numerator) tells us HOW MANY pieces we have. The bottom number (Denominator, 'D' for Down) tells us the TOTAL number of pieces the whole object was cut into."
            },
            {
                "id": "FRAC_EQUIVALENT_ADD_RULE",
                "name": "Not understanding equivalent fractions",
                "description": "Believing that multiplying or dividing numerator and denominator changes the value, or adding a constant to both.",
                "example": "Thinking 2/4 is twice as large as 1/2.",
                "remediation_strategy": "Visual bar modeling: 1 half-cup of water is exactly equal to 2 quarter-cups.",
                "default_simple_explanation": "If you cut a half roti into two equal pieces, you have 2 fourths (2/4), but the total amount of roti is still the same as 1 half (1/2)! They are equivalent fractions."
            }
        ]
    },
    "Place value": {
        "description": "Base-10 positional notation, face value vs place value, and decimals.",
        "misconceptions": [
            {
                "id": "PV_FACE_VS_PLACE",
                "name": "Confusing face value with place value",
                "description": "Treating the digit as just its face value without considering its column position.",
                "example": "In 472, stating the value of 7 is just 7 instead of 70.",
                "remediation_strategy": "Currency note model: 7 in the tens place is like having 7 ten-rupee notes (70 rupees), not 7 one-rupee coins.",
                "default_simple_explanation": "In 472, the digit 7 is sitting in the Tens place. Its face value is 7, but its place value is 7 x 10 = 70 rupees! Always multiply the digit by the value of its room."
            },
            {
                "id": "PV_INDEPENDENT_DIGITS",
                "name": "Reading digits independently rather than as composite value",
                "description": "Viewing a multi-digit number as individual disconnected single digits.",
                "example": "Writing 'four hundred five' as 4005 instead of 405.",
                "remediation_strategy": "Expanded form cards: 400 + 0 + 5 overlaps together to form 405.",
                "default_simple_explanation": "Numbers use place values like seats in a train. The hundreds seat has 4, the tens seat has 0, and the ones seat has 5. Together they sit as 405, not 4005!"
            },
            {
                "id": "PV_DECIMAL_LONGER_IS_LARGER",
                "name": "Treating decimal parts as regular whole numbers",
                "description": "Believing 0.45 is larger than 0.7 because 45 is larger than 7.",
                "example": "Claiming 0.19 > 0.4.",
                "remediation_strategy": "Tenths vs hundredths: 0.4 is 4 tenths (40 hundredths), which is larger than 19 hundredths.",
                "default_simple_explanation": "Look at the tenths place right after the decimal point! 0.4 is 4 tenths, which is 40 hundredths. 0.19 is only 19 hundredths. 40 is bigger than 19, so 0.4 is bigger than 0.19!"
            }
        ]
    }
}

def get_taxonomy_summary():
    """Returns a flat list of all taxonomies for prompt injection."""
    summary = []
    for skill, data in TAXONOMY.items():
        for item in data["misconceptions"]:
            summary.append({
                "skill": skill,
                "category": item["id"],
                "name": item["name"],
                "description": item["description"],
                "example": item["example"],
                "strategy": item["remediation_strategy"]
            })
    return summary
