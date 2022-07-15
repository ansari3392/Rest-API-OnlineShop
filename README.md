# Rest-API-OnlineShop


how to run?
1. Enter your database credentials in karisma_shop/settings.py
2. Enter a broker url for celery in karisma_shop/settings.py
3. Run python manage.py migrate
4. Run python manage.py runserver
5. Run celery worker: celery -A karisma_shop worker -l info -P gevent
6. Run celery beat: celery -A karisma_shop beat -l info -S django
