# Основные компоненты:
## backend.api - основной сервис, работающий в постоянном режиме, отвечая на запросы клиентов, демо настройки в .env-dist (взаимодействие через Makefile)
## backend.app - конфигурация nginx
## backend.investments_src - сервис запускающийся каждые 6 часов (конфигурируется в docker-compose всего проекта в backend) (взаимодействие через Makefile)
## logs - логи nginx
## static - статический контент, раздаваемый nginx для его оптимизации.
## Все оркеструется docker-compose.yaml файлом.