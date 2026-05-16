import pandas as pd
import numpy as np

def load_data(file_path='dataset_financier.csv'):
    df = pd.read_csv(file_path, encoding='utf-8')
    
    # Colonnes en minuscule
    df.columns = df.columns.str.lower().str.strip()
    
    # Remplacer Société générale par SG
    df['banque'] = df['banque'].replace('Société générale', 'SG')
    
    # Ratios financiers
    df['rentabilite']  = df['revenu'] / df['actifs']
    df['marge_nette']  = (df['revenu'] - df['depenses']) / df['revenu']
    df['liquidite']    = df['flux_tresorerie'] / df['depenses']
    df['levier']       = df['bilan_financier'] / df['capital']
    df['efficacite']   = df['depenses'] / df['revenu']
    
    # Écart à la moyenne par banque
    df['ecart_revenu'] = df['revenu'] - df['revenu'].mean()
    
    return df

def get_kpis(df):
    return {
        'revenu_total'   : df['revenu'].sum(),
        'capital_moyen'  : df['capital'].mean(),
        'flux_moyen'     : df['flux_tresorerie'].mean(),
        'taux_moyen'     : df['taux_interet'].mean()
    }

def get_diverging(df):
    ecarts = df.groupby('banque')['revenu'].sum()
    moyenne = ecarts.mean()
    return (ecarts - moyenne).sort_values()

def get_dotplot(df, ville='Bafoussam'):
    return df[df['lieu'] == ville].groupby('banque')['revenu'].sum().sort_values(ascending=False)

def get_heatmap(df):
    pivot = df.groupby(['lieu', 'banque'])['revenu'].sum().unstack()
    moyenne = pivot.mean().mean()
    return (pivot - moyenne).round(2)

def get_radar(df):
    return df.groupby('banque')[['rentabilite', 'marge_nette',
                                  'liquidite', 'levier', 'efficacite']].mean()

def get_scatter(df):
    return df[['banque', 'revenu', 'depenses']]

def get_agence_grouped(df):
    """Revenus par agence groupés par banque"""
    return df.groupby(['banque', 'agence'])['revenu'].sum().unstack()

def get_violin_data(df):
    """Distribution du taux d'intérêt par banque"""
    return df[['banque', 'taux_interet']]

def get_diverging_ville(df):
    """Écart à la moyenne par ville"""
    ecarts = df.groupby('lieu')['revenu'].sum()
    moyenne = ecarts.mean()
    return (ecarts - moyenne).sort_values()

def get_dotplot_comparatif(df):
    """Dot plot comparatif pour 4 villes principales"""
    villes_principales = df['lieu'].unique()[:4]
    result = {}
    for ville in villes_principales:
        result[ville] = df[df['lieu'] == ville].groupby('banque')['revenu'].sum()
    return result

def get_portfolio_health(df):
    """Calcul du Portfolio Health"""
    rentabilite_moyenne = df['rentabilite'].mean()
    liquidite_moyenne = df['liquidite'].mean()
    health = (rentabilite_moyenne * 50 + liquidite_moyenne * 50)
    return min(100, max(0, health))

def get_market_risk(df):
    """Calcul du Market Risk"""
    volatilite = df['revenu'].std()
    moyenne = df['revenu'].mean()
    risk = (volatilite / moyenne) * 100
    return min(100, max(0, risk))