# 🐾 Animal Shelter Walk Scheduler

A Django web application that lets users schedule walks with animals from a local animal shelter. The app helps shelters manage their animals, volunteers, and daily walk bookings in one place — making it easier for animals to get the exercise and human contact they need.

## ✨ Features

The application provides three separate panels, each tailored to a different type of user:

- **Customer panel** — browse animals available for walks, book a walk slot, and manage your upcoming and past walks.
- **Employee panel** — manage animals in the shelter (add, edit, mark as adopted), oversee walk bookings, and handle day-to-day operations.
- **Admin panel** — full system administration: manage users, categories, employees, and all data in the system.

## 🛠️ Tech Stack

- **Backend:** Django (Python)
- **Database:** MySQL
- **Containerization:** Docker / Docker Compose

The entire application (Django app + MySQL database) runs inside Docker containers, so you don't need to install Python, MySQL, or any dependencies on your machine.

## 🚀 Getting Started

### Prerequisites

You only need one thing installed on your computer:

- **Docker Desktop** — download and install it from [docker.com](https://www.docker.com/products/docker-desktop/).

Make sure Docker Desktop is **running** before you continue (look for the whale icon in your system tray / menu bar).

### Running the App

1. **Clone or download the project** to your computer.

2. **Open a terminal** and navigate into the project folder (the one containing `docker-compose.yml`):

   ```bash
   cd path/to/project
   ```

3. **Build and start the containers:**

   ```bash
   docker compose up --build
   ```

   The first run will take a few minutes — Docker needs to download images and install dependencies. Subsequent runs will be much faster.

4. **Open the app in your browser:**

   ```
   http://localhost:8000
   ```

### Stopping the App

Press `Ctrl + C` in the terminal where the containers are running, then run:

```bash
docker compose down
```

This stops and removes the containers (your database data is preserved in a Docker volume).

## 🧰 Useful Commands

| Command | What it does |
|---|---|
| `docker compose up --build` | Build images and start the app |
| `docker compose up` | Start the app (no rebuild) |
| `docker compose down` | Stop and remove containers |
| `docker compose logs -f` | Follow the application logs |
| `docker compose exec web bash` | Open a shell inside the Django container |

## 📝 Notes

- If port `8000` is already in use on your machine, edit the `ports` section in `docker-compose.yml` to map a different host port.
- The MySQL database is persisted in a Docker volume, so your data survives container restarts.
- On older Docker installations the command is `docker-compose` (with a hyphen) instead of `docker compose`.
