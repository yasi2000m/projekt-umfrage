# MeinungsWelle – Streamlit-Umfrage-App

Eine moderne Umfrageplattform mit öffentlicher Benutzeransicht und passwortgeschützter Admin-Zentrale.

## Funktionen

- Umfragen mit Einfach- oder Mehrfachauswahl erstellen
- beliebig viele Fragen und Antwortoptionen
- bestehende Umfragen bearbeiten und dauerhaft löschen
- Umfragen aktivieren oder pausieren
- farbige Auswertung mit Tabellen und Balkendiagrammen
- SQLite-Datenbank für Umfragen und Antworten
- responsive Benutzeroberfläche mit eigener Hero-Illustration

## Lokal starten

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Der Adminbereich ist oben rechts erreichbar. Das voreingestellte Passwort ist `7777`.

## Passwort sicher hinterlegen

```bash
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
```

Danach das Passwort in `.streamlit/secrets.toml` ändern. Diese Datei wird nicht zu Git hochgeladen.

## Streamlit Community Cloud

1. Projekt in ein GitHub-Repository pushen.
2. Auf [Streamlit Community Cloud](https://share.streamlit.io/) eine App anlegen.
3. Als Main file `app.py` auswählen.
4. Unter **App settings → Secrets** ein Admin-Passwort eintragen:

   ```toml
   ADMIN_PASSWORD = "dein-sicheres-passwort"
   ```

5. Deployen und den erzeugten Link teilen.

## Speicherung

SQLite ist für lokale Tests und kleine Demos geeignet. Das Dateisystem von Streamlit Community Cloud ist nicht als dauerhafte Datenbank gedacht; bei Neustarts oder Deployments können Antworten verloren gehen. Für eine langfristige öffentliche Nutzung sollte später PostgreSQL, Supabase oder Neon angebunden werden.
