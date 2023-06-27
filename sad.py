import telebot
from telebot import types
import sqlite3

TOKEN = "6284854329:AAFBmjxT_qhdgQn9JRQzh9xJFBgrsTDHUXc" #Inserire il token
PosizioneDB = r"DataBaser.db" #Inserisci la directory dove si ha salvato il DataBase

bot = telebot.TeleBot(TOKEN, parse_mode=None)
lista = ['bussolengo','castelnuovo','lazise','mozzecane','pastrengo','pescantina','sommacampagna','sona','valeggio','vigasio','villafranca']
strdilista='Bussolengo, Castelnuovo, Lazise, Mozzecane, Pastrengo, Pescantina, Sommacampagna, Sona, Valeggio, Vigasio, Villafranca'
tipi = ['culturale','sportiva','volontariato','di categoria e sindacali', "d'arma",'arma','sociale','comitato di quartiere','associativa','assistenziale','ricreativa','associazione di danza', 'circolo parrochiale', 'associazione scout', 'polisportiva', 'ass. sportiva', 'impianto sportivo privato', 'palestra privata', 'ass. socio assistenziale', 'ass. diverse abilità','ass. famiglia','ass. giovanile']
strditipi = "Culturale, Sportiva, Volontariato, Di categoria e sindacali, D'arma, Arma, Sociale, Comitato di quartiere, Associativa, Assistenziale, Ricreativa, Associazione di danza, Circolo parrochiale, Associazione scout, Polisportiva, Ass. Sportiva, Impianto Sportivo Privato, Palestra Privata, Ass. Socio Assistenziale, Ass. Diverse Abilità, Ass. Famiglia, Ass. Giovanile"


#Il bot funziona solo per 1 utente alla volta, necessita o la riscrizione di tutto il codice, o la scrittura di una nuova classe che ha come attributo lo userID
def setstep(valore):
    global step
    step=valore

def esistenza_tipo_associazione(messaggio):
    if messaggio.text.lower() in tipi:
        return True

def esistenza_nome_comune(messaggio):
    if messaggio.text.lower() in lista:
        return True
    
@bot.message_handler(commands=['start'])
def sendmessage(message):
    
    setstep(0)
    bot.send_message(message.chat.id, "Benvenuto al bot delle Associazioni! Perfavore inserisci un comune.")

@bot.message_handler(content_types=['text'])
def sendmessage(message):
    
    if esistenza_nome_comune(message) and step==0:
        setstep(1)
        global selezione
        selezione = message.text
        bot.send_message(message.chat.id, "Seleziona il tipo di associazione alla quale sei interessato.")
        con = sqlite3.connect(PosizioneDB)
        cur = con.cursor()
        global resu
        resu = cur.execute('SELECT Tipo FROM associazioni_'+selezione)
        resu=resu.fetchall()
        bot.send_message(message.chat.id, "I tipi disponibili sono: "+str(set(resu)).replace('[','').replace('(','').replace(']','').replace("'",'').replace(')','').replace('{','').replace('}',''))
        #Alcuni nomi vengono visualizzati in modo strano, ad esempi le associazioni di tipo "D'Arma", ovviamente venendo rimmose le "'", vengono visualizzate come Darma
        #Alcune volte I tipi di alcune assocaizioni non vengono chiamate nel file .db
        return None
    elif step==0:
        bot.send_message(message.chat.id, "Seleziona uno tra i seguenti comuni: "+strdilista)

    if step==1 and esistenza_tipo_associazione(message):
        setstep(2)
        con = sqlite3.connect(PosizioneDB)
        cur = con.cursor()
        global record
        record = cur.execute('SELECT nome_associazione FROM associazioni_'+selezione+' WHERE Tipo = "'+message.text.rstrip().title()+'"')
        record=record.fetchall()
        if len(record) == 0:
            bot.send_message(message.chat.id, 'Non esistono risultati secondi i tuoi criteri di ricerca.')
            setstep(1)
        else:
            bot.send_message(message.chat.id, 'Ecco una lista di Associazioni secondo i tuoi criteri di ricerca: '+str(record).replace('[','').replace('(','').replace(']','').replace(')','').replace("'",''))
            bot.send_message(message.chat.id, 'Scegline una')
        return None
        
    if step==2 and message.text.lower().rstrip() in str(record).lower():
        markup = types.ReplyKeyboardMarkup(row_width=3)
        itembtn1 = types.KeyboardButton('Direzioni per andarci.')
        itembtn2 = types.KeyboardButton('Ottenere info')
        itembtn3 = types.KeyboardButton('Controllare gli Eventi')
        markup.add(itembtn1, itembtn2, itembtn3)
        bot.send_message(message.chat.id, 'Cosa vuoi fare?', reply_markup = markup)
        global nomeass
        nomeass = message.text
        setstep(3)
    elif step==2 and not esistenza_tipo_associazione(message):
        bot.send_message(message.chat.id, 'Non hai inserito un nome valido')
        
    if step==3:
        con = sqlite3.connect(PosizioneDB)
        cur = con.cursor()
        record = cur.execute('SELECT Indirizzo FROM associazioni_'+selezione+' WHERE nome_associazione = "'+nomeass.rstrip().title()+'"')
        record = record.fetchall()
        
        #alcune volte nel file SQL, non ri riesce ad accedere all'indirizzo di alcune associazioni, dato la nomenclatura fatta a caso (necessita modifica delle entry nel DB)
        if message.text == 'Direzioni per andarci.':
            bot.send_message(message.chat.id,'maps.google.com/maps?daddr='+str(record).replace(' ', '+').replace('[','').replace('(','').replace(']','').replace(')','').replace("'",'')+'+'+selezione,reply_markup=False)
        elif message.text == 'Ottenere info':
            bot.send_message(message.chat.id,record,reply_markup=False)
        elif message.text == 'Controllare gli Eventi':
            bot.send_message(message.chat.id,'Lista eventi: https://calendar.google.com/calendar/u/0?cid=aXN0ZjQxNTMyQGdtYWlsLmNvbQ',reply_markup=False)
            
bot.infinity_polling()
