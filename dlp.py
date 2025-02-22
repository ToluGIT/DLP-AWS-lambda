import random
from datetime import datetime

def calculate_luhn_digit(partial_number):
    total = 0
    reversed_digits = list(map(int, reversed(partial_number)))
    for i, digit in enumerate(reversed_digits):
        if i % 2 == 0:
            doubled = digit * 2
            total += (doubled // 10) + (doubled % 10)
        else:
            total += digit
    check_digit = (10 - (total % 10)) % 10
    return check_digit

def generate_card_number(card_type):
    card_config = {
        'American Express': {
            'prefixes': ['34', '37'],
            'length': 15,
            'cvv_length': 4
        },
        'Mastercard': {
            'prefixes': ['51', '52', '53', '54', '55'],
            'length': 16,
            'cvv_length': 3
        }
    }
    config = card_config[card_type]
    prefix = random.choice(config['prefixes'])
    remaining_length = config['length'] - len(prefix) - 1
    partial_number = prefix + ''.join([str(random.randint(0, 9)) for _ in range(remaining_length)])
    check_digit = calculate_luhn_digit(partial_number)
    return partial_number + str(check_digit)

def generate_exp_date():
    now = datetime.now()
    current_year = now.year
    year = random.randint(current_year + 1, current_year + 5)
    month = random.randint(1, 12)
    return f"{month:02d}/{year % 100:02d}"

def generate_cvv(length):
    return ''.join([str(random.randint(0, 9)) for _ in range(length)])

def generate_pii_entry(card_type):
    number = generate_card_number(card_type)
    exp_date = generate_exp_date()
    cvv_length = card_config[card_type]['cvv_length']
    cvv = generate_cvv(cvv_length)
    
    entry = []
    if card_type == 'American Express':
        entry.append(f"{card_type}")
        entry.append(f"{number} {exp_date}")
        entry.append(f"CCV: {cvv}")
    elif card_type == 'Mastercard':
        entry.append(f"{card_type}")
        entry.append(f"{number}")
        entry.append(f"Exp: {exp_date}")
        entry.append(f"Security code: {cvv}")
    return entry

card_config = {
    'American Express': {
        'prefixes': ['34', '37'],
        'length': 15,
        'cvv_length': 4
    },
    'Mastercard': {
        'prefixes': ['51', '52', '53', '54', '55'],
        'length': 16,
        'cvv_length': 3
    }
}

if __name__ == "__main__":
    entries = []
    
    # Generate American Express
    entries.extend(generate_pii_entry('American Express'))
    entries.append('')
    
    # Generate Mastercard
    entries.extend(generate_pii_entry('Mastercard'))
    entries.append('')
    
    # Generate another American Express
    entries.extend(generate_pii_entry('American Express'))
    
    print('\n'.join(entries))
