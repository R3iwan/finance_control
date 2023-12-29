import telebot
import sqlite3

conn = sqlite3.connect('finance_control.db')

cursor = conn.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS expenses (
                    id INTEGER PRIMARY KEY,
                    user_id INTEGER,
                    amount REAL,
                    category TEXT
                 )''')

conn.commit()
conn.close()

TOKEN = 'YOUR_TOKEN'
bot = telebot.TeleBot(TOKEN)

expenses = []
budget = 0

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, 'Hello! I am your bot')

@bot.message_handler(commands=['setbudget'])
def setbudget(message):
    global budget
    try:
        budget = float(message.text.split()[1])
        bot.reply_to(message, f"Budget set to: {budget}")
    except(ValueError, IndexError):
        bot.reply_to(message, "Usage: /setbudget <amount>")

@bot.message_handler(commands=['report'])
def expense_report(message):
    user_id = message.from_user.id
    conn = sqlite3.connect('finance_control.db')
    cursor = conn.cursor()

    cursor.execute("SELECT amount, category FROM expenses WHERE user_id = ?", (user_id,))
    expenses = cursor.fetchall()

    report = "Expense Report:\n"
    total = 0
    for amount, category in expenses:
        report += f"{category}: {amount}\n"
        total += amount

    report += f"Total Expenses: {total}"
    bot.reply_to(message, report)
    conn.close()    

@bot.message_handler(commands=['clear'])
def clear_expenses(message):
    user_id = message.from_user.id

    conn = sqlite3.connect('finance_control.db')
    cursor = conn.cursor()

    cursor.execute("DELETE FROM expenses WHERE user_id = ?", (user_id,))

    conn.commit()
    conn.close()

    bot.reply_to(message, "All your expenses have been cleared!")

@bot.message_handler(func=lambda m: True)
def record_expanses(message):
    try:
        user_id = message.from_user.id
        amount, category = message.text.split()
        amount = float(amount)

        conn = sqlite3.connect('finance_control.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO expenses (user_id, amount, category) VALUES (?, ?, ?)",
                       (user_id, amount, category))
        conn.commit()
        conn.close()

        expenses.append((amount,category))
        bot.reply_to(message, f"Recorded {amount} for {category}")
        
        total_expenses = sum([exp[0] for exp in expenses])

        response = f"Expense recorded: {amount} for {category}. "
        if total_expenses > budget:
            response += "Warning: You've exceeded your budget!"
        elif total_expenses / budget > 0.9:  
            response += "Alert: You're close to reaching your budget limit!"

    except ValueError:
        bot.reply_to(message, "Please enter in format: amount category") 

bot.polling()

