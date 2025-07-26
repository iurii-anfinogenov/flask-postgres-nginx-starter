# 📦 Ansible Lite — деплой Flask-приложения без Docker

Ветка `ansible-lite` предназначена для развёртывания Flask-приложения с помощью **Ansible**, без использования Docker.  
Проект подключается к **внешней базе PostgreSQL** и разворачивается на сервере Ubuntu с nginx + gunicorn.

---

## 🚀 Быстрый старт

1. Настройте инвентарь в `inventory/hosts.ini`
2. Убедитесь, что SSH-ключ проброшен
3. Запустите:

```bash
ansible -i inventory/hosts.ini all -m ping
ansible-playbook -i inventory/hosts.ini playbook.yml

📂 Структура
├── inventory/hosts.ini         # Инвентарь с описанием хоста
├── files/env.example           # Пример .env
├── templates/gunicorn.service.j2  # systemd unit
├── playbook.yml                # Главный Ansible playbook
└── README.md

🔧 Требования

    Ubuntu 22.04 на удалённом сервере

    Внешний PostgreSQL (без установки в этом уроке)

    SSH-доступ по ключу

    Ansible >= 2.15 на управляющей машине

    📝 Примечания

    Приложение клонируется из ветки main этого же репозитория

    Ветка предназначена для обучения и первых шагов в Ansible

    Используется встроенный pip и systemd без ролей

