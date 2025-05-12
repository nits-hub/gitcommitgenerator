# 📝 Git Commit Report Generator (DRF)

This project is a **Django REST Framework-based API** that generates a **Git commit report** from a given Git repository URL between a specified date range. It supports pulling commit data from **all branches**, or optionally a specific branch, and outputs the result in either **JSON** or **Markdown** format.

---

## 🚀 Features

- Clone or reuse a Git repository
- Extract commit logs from **all remote branches**
- Filter commits by:
  - Date range (`start_date`, `end_date`)
  - Author (optional future feature)
- Export commit report in:
  - JSON
  - Markdown (for readability and documentation)
- No database storage required
- Simple and lightweight setup

---

## 🛠️ Technology Stack

- **Backend Framework:** Django 5.2 + Django REST Framework
- **Version Control Parser:** [GitPython](https://gitpython.readthedocs.io/en/stable/)
- **Python Version:** Python 3.10+