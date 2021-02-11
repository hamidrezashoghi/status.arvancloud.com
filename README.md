# status.arvancloud.com
Monitoring Arvancloud services and infra [https://status.arvancloud.com](https://status.arvancloud.com) with alertmanager

How to install:
```
git clone https://github.com/hamidrezashoghi/status.arvancloud.com.git
sudo su -
pip3 install --upgrade pip
pip3 install -r requirements.txt
cp -rv status.arvancloud.com /opt
cp arvan_monitoring.service /lib/systemd/system/
chown root:root /lib/systemd/system/status_monitoring.service
chmod 0644 /lib/systemd/system/status_monitoring.service
```

Change alertmanager URL:
```
vim status.arvancloud.com/arvan_status_monitoring/spiders/status_monitoring_.py
go to line 33 and change address
host = 'https://your_alertmanager/api/v1/alerts'
```

How to run:
```
scrapy crawl status_monitoring
```