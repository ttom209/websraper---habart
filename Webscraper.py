"""
projekt_3.py: třetí projekt
author: Tomáš Habart
email: tomhabart@seznam.cz
"""

# Importy
import requests
from bs4 import BeautifulSoup
import argparse

# Funkce pro sestavení úplné URL z relativní URL
def sestav_url(base_url, relative_url):
    if '/' in base_url:
        return base_url[:base_url.rfind('/')] + "/" + relative_url
    return base_url

# Funkce pro získání názvů stran z dané URL
def ziskej_nazvy_stran(stranky_url):
    response = requests.get(stranky_url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        radky = soup.find_all('tr')
        seznam_stran = []
        for radek in radky:
            bunky = radek.find_all("td")
            if len(bunky) == 5:
                nazev_strany = bunky[1].get_text().strip()
                if nazev_strany not in seznam_stran:
                    seznam_stran.append(nazev_strany)
        return seznam_stran
    else:
        print("Nepodařilo se stáhnout data")
        return []

# Funkce pro zpracování hlavních dat z první URL
def zpracuj_data(prvni_url, soubor, strany_url):
    response = requests.get(prvni_url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        radky = soup.find_all('tr')
        with open(soubor, 'w', encoding='cp1250') as f:
            seznam_stran = ziskej_nazvy_stran(strany_url)
            f.write("Kod oblasti;Nazev oblasti;Registrovany volici;Obalky;Platné hlasy;")
            f.write(";".join(seznam_stran) + "\n")
            for radek in radky:
                bunky = radek.find_all("td")
                if len(bunky) >= 2:
                    prvni_bunka, druha_bunka = bunky[:2]
                    odkazy = prvni_bunka.find_all("a")
                    if odkazy:
                        relativni_url = odkazy[0].get('href')
                        druha_url = sestav_url(prvni_url, relativni_url)
                        radek_data = f"{prvni_bunka.get_text().strip()};{druha_bunka.get_text().strip()}"
                        seznam_stran = zpracuj_podrobnosti(druha_url, f, radek_data, seznam_stran)
    else:
        print("Nepodařilo se stáhnout data")

# Funkce pro zpracování podrobných dat z druhé URL
def zpracuj_podrobnosti(druha_url, soubor, radek_data, seznam_stran):
    response = requests.get(druha_url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        radky = soup.find_all('tr')
        radek_info = ""
        seznam_hlasu = []
        for radek in radky:
            bunky = radek.find_all("td")
            if len(bunky) == 9:
                prvni_bunka, druha_bunka, platne_hlasy_bunka = bunky[3], bunky[4], bunky[5]
                radek_info = f"{prvni_bunka.get_text().strip()};{druha_bunka.get_text().strip()};{platne_hlasy_bunka.get_text().strip()}"
            elif len(bunky) == 5:
                nazev_strany = bunky[1].get_text().strip()
                hlasy_strany = bunky[2].get_text().strip()
                if nazev_strany not in seznam_stran:
                    seznam_stran.append(nazev_strany)
                seznam_hlasu.append(hlasy_strany)
        soubor.write(f"{radek_data};{radek_info};{';'.join(seznam_hlasu)}\n")
        return seznam_stran
    else:
        print("Nepodařilo se stáhnout data")
        return seznam_stran

# Hlavní funkce skriptu
def hlavni(url, soubor):
    pevna_strany_url = "https://volby.cz/pls/ps2017nss/ps311?xjazyk=CZ&xkraj=12&xobec=506761&xvyber=7103"
    zpracuj_data(url, soubor, pevna_strany_url)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Skript pro web scraping')
    parser.add_argument('url', type=str, help='URL stránky pro stažení')
    parser.add_argument('soubor', type=str, help='Výstupní soubor')
    args = parser.parse_args()
    hlavni(args.url, args.soubor)
