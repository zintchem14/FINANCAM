import requests

def get_taux_change():
    try:
        response = requests.get("https://api.exchangerate-api.com/v4/latest/USD")
        data = response.json()
        usd_fcfa = data['rates']['XAF']
       
        response2 = requests.get("https://api.exchangerate-api.com/v4/latest/EUR")
        data2 = response2.json()
        eur_fcfa = data2['rates']['XAF']
       
        return {
            'usd_fcfa': round(usd_fcfa, 0),
            'eur_fcfa': round(eur_fcfa, 0)
        }
    except:
        return {'usd_fcfa': 610, 'eur_fcfa': 655}