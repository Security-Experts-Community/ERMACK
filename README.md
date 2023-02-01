# ERM&CK Enterprise Response Model & Common Knowledge

## Введение

ERMACK - это общедоступная база знаний по реагированию. В основе этой базы знаний лежит модель, которая позволяет связать между собой сущности и их связи. По сути это онтология домена реагирования. Дополняя и развивая эту модель сообщество может оцифровывать свои экспертные знания для дальнейшей автоматизации рутинных задач.

Проект ERMACK является форком проекта RE&CT с иным взглядом на архитектуру и кейсы применения.

Основным отличием и нововведением проекта относительно RE&CT является большая детализация действий реагирования. Мы планируем собирать конкретные реализации действий реагирования для того чтобы при возникновении инцидента, у пользователя были конкретные инструкции к действию, а не абстрактные рекомендации. Такие рекомендации затем нужно приземлять на свою систему и искать инструкцию в открытых источниках в Интернете. Наш подход предполагает, что все конкретные инструкции будут описаны в рамках единой базы знаний и провалидированы участниками комьюнити. Таким образом на выходе получается провалидированная и одобренная сообществом база знаний по реагированию.


## Основные цели проекта:
1) Предоставить пользователю удобный инструмент для подготовки инфраструктуры к процессам реагирования на компьютерные инциденты
2) Предоставить пользователю информацию о действиях в той или иной ситуации
3) Автоматизация построения сценариев реагирования, аналитика над данными


## Репозитории проекта
Основной:
- GitHub: https://github.com/Security-Experts-Community/ERMACK

Зеркала:
- Codeberg: https://codeberg.org/Security-Experts-Community/ERMACK
- GitFlic: https://gitflic.ru/project/security-experts-community/ermack


## Использование базы знаний
### Поиск по публичной версии сайта
Самый простой способ ознакомиться с текущем наполнением базы знаний - перейти по [ссылке][1] . Это текущая версия базы знаний, которая собирается при каждом новом изменении в ветке `master` [репозитория на GitHub][2]


### Запуск локальной копии базы знаний
Для запуска локальной версии базы занний или применения скриптов аналитики необходимо скачать [репозиторий с GitHub][2].

**Алгоритм**:
1. Скачиваем репозиторий

1. Вносим изменения в файл конфигурации

1. Создаём файл с профилем инфраструктуры

1. Переходим в корень проекта

1. Создаём Docker-образ
`docker build -t sec/ermack .`

1. Запускаем контейнер из собранного образа
`docker run --rm -it -p 8000:8000 sec/ermack`

1. Переходим по ссылке http://localhost:8000
![Main ERMACK Page](assets/main_page_ru.png)



---
[1]: https://ermack.github.io
[2]: https://github.com/Security-Experts-Community/ERMACK
