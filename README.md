# Laptop Price Predictor

Ovaj projekt je napravljen za potrebe kolegija "Računarstvo usluga i analiza podataka".
U ovom projektu se radi o web aplikaciji koja je razvijena pomoću **Streamlita** (Python razvojni okvir otvorenog koda) koja omogućuje korisnicima unos specifikacija laptopa te automatsku predikciju njegove cijene. 
Model stojnog učenja, hostan je na Azure Machine Learning platformi, obrađuje unesene podatke i vraća predviđenu cijenu. 
Aplikacija također nudi interaktivne grafikone za analizu podataka i trendova.

### Korišteni alati i tehnologije
1. [**Python**](https://www.python.org/) - glavni programski jezik
2. [**Streamlit**](https://streamlit.io/) - razvoj web sučelja
3. [**Pandas**](https://pandas.pydata.org/) - obrada i analiza podatkovnog skupa
4. [**Plotly Express**](https://plotly.com/python/plotly-express/) - izrada interaktivnih grafikona
5. [**Azure Machine Learning**](https://azure.microsoft.com/en-us/products/machine-learning) - za izradu i hostanje modela strojnog učenja

### Korišteni alati i tehnologije
- **Autentifikacija korisnika**: Jednostavan sustav prijave i registracije putem forme u bočnom panelu
- **Unos specifikacija prijenosnog računala**: Intuitivno korisničko sučelje za unos specifikacija prijenosnog računala
- **Predviđanje cijene**: Integracija s modelom strojnog učenja na Azure Machine Learning platformi koji vraća predviđenu cijenu
- **Vizualizacija podataka**: Interaktivni grafikoni (stupčasti dijagram, dijagram raspršenosti, itd.) koji prikazuju analizu kao što su prosječna cijena svakog brenda, odnos cijene prijenosnog računala i količine radne memorije koju sadrži i brojni drugi

### Instalacija i pokretanje

*Radi jednostavnosti korišenja aplikacije, nakon pokretanja potrebno se prijaviti u sustav sa sljedećim podacima:*
   ```bash
    Username: test
    Password: test
   ```

#### Opcija 1: Pristupanje aplikaciji deployanoj na webu:
1. Kliknuti na sljedeći link: **https://ruaproject.streamlit.app/**
2. Prijaviti se u sustav s gore navedenim podacima

#### Opcija 2: Lokalno pokretanje: 
1. Klonirajte repozitorij:
   ```bash
    git clone https://github.com/vaše-korisničko-ime/laptop-price-predictor.git
    cd laptop-price-predictor
   ```

2. Instalirajte potrebe pakete:
   ```bash
    pip install -r requirements.txt
   ```
   
3. Pokrenite aplikaciju:
   ```bash
    streamlit run app.py
   ```
4. Prijaviti se u sustav s gore navedenim podacima

### Korištenje web aplikacije: 
- Autentifikacija: Prijavite se ili registrirajte putem forme
- Unos podataka: Unesite specifikacije prijenosnog računala u glavnu formu aplikacije
- Predviđanje cijene: Kliknite na "Submit" gumb kako biste poslali podatke modelu strojnog učenja i dobili ispis predviđene cijene
- Vizualizacija: Pregledajte interaktivne grafikone u bočnom panelu koji se automatski ažuriraju prema novim unosima korisnika

### Poznati problemi koji se mogu pojaviti:
- Provjerite da su verzije Pythona i potrebnih paketa u skladu s verzijama propisani *requirements.txt* datotekom
- Ovisno o putanji gdje je Python instaliran na računalu korisnika koji želi lokalno pokrenuti web aplikaciju, možda će biti potrebno aplikaciju pokrenuti s naredbom
    ```bash
  python -m streamlit run app.py
   ```
- Zbog tromosti sustava na kojem je aplikacija pokrenuta, postoji mogućnost da će biti potrebno 2 puta kliknuti na gumb *"Sign In"* ili *"Log In"* prilikom registracije, odnosno prijave u sustav (isto vrijedi i za *"Log Out"* gumb prilikom odjave iz sustava)

###### Adrian Horvat & Karlo Šibalić, 1.g DRC