# Foodora Clone

A full-stack food delivery platform modelled after Foodora/Wolt. Covers the complete order lifecycle — from customer browsing to courier delivery — with real routing via GraphHopper.

---

## Features

**Customer flow**
- Browse restaurants and menus
- Place and track orders in real time
- Order history and account management

**Restaurant portal**
- Menu management (items, pricing, availability)
- Incoming order dashboard with accept/reject controls

**Courier portal**
- Active delivery assignment and status updates
- Route calculation via GraphHopper (real road network routing)

**Platform**
- Session-based authentication with secure token handling
- Rate limiting on all API endpoints (Flask-Limiter)
- Multi-blueprint architecture: user, delivery, and admin services separated
- YAML-driven configuration — no hardcoded values
- MySQL + SQLite support

---

## Architecture

```
main.py
├── user_webserver.py      ← customer routes (blueprint)
├── delivery_webserver.py  ← courier routes (blueprint)
├── admin_webserver.py     ← restaurant/admin routes (blueprint)
├── auth.py                ← session + token auth
├── user_manager.py        ← user CRUD
├── order_manager.py       ← order lifecycle
├── delivery_manager.py    ← courier assignment
├── routing.py             ← GraphHopper integration
└── database.py            ← DB connection + queries
```

---

## Tech stack

| Layer | Technology |
|---|---|
| Backend | Python, Flask |
| Routing engine | [GraphHopper](https://github.com/graphhopper/graphhopper) |
| Database | MySQL / SQLite |
| Auth | Session-based + token auth |
| Rate limiting | Flask-Limiter |
| Config | YAML |

---

## Setup

**1. Install dependencies**
```bash
pip install -r requirements.txt
```

**2. Configure**
```bash
cp config/default_config.yml config/configuration.yml
# Edit configuration.yml — set DB credentials, routing service, etc.
```

**3. (Optional) Start GraphHopper**

For real road-network routing, download a GraphHopper JAR and an OSM `.pbf` file for your region, place them in `graphhoper/`, then run:
```bash
java -Ddw.graphhopper.datareader.file=<region>.osm.pbf \
     -jar graphhopper-web-10.0.jar server config-example.yml
```

**4. Run**
```bash
python setup.py    # first-time DB init
python main.py
```

---

## Configuration (`config/configuration.yml`)

```yaml
routing:
  service: graphhopper   # or "osrm"

database:
  host: localhost
  port: 3306
  name: foodora
  user: root
  password: ""
```
