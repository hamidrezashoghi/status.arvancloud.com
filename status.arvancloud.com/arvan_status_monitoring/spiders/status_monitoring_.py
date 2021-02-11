# -*- coding: utf-8 -*-
import scrapy
import os
import json
from alertmanager import AlertManager
from alertmanager import Alert
import time
import re
import yaml    

class StatusMonitoringSpider(scrapy.Spider):
    name = 'status_monitoring'
    allowed_domains = ['https://status.arvancloud.com']
    start_urls = ['https://status.arvancloud.com/']


    # service or infra name, service of infra status, current_time(when happen)
    list_of_alerts = []

    def alerting(self, svc_inf_name, svc_inf_status):
        data = {
            "labels": {
                "alertname": "Arvancloud services status",
                "instance": svc_inf_name,
                "severity": "critical",
                #"team": "test"
            },
            "annotations": {
                "description": svc_inf_name + " has " + "'" + svc_inf_status + "'" + "<br>",
                "summary": "Arvancloud has incident in their services or infra"
            }
        }
        host = 'https://your_alertmanager/api/v1/alerts'
        a_manager = AlertManager(host=host)
        a_manager.post_alerts(data)

    def parse(self, response):
        print("processing: " + response.url)

        service_name = response.css(".service-status--name::text").extract()
        service_status = response.css(".service-status--status::text").extract()

        row_name = zip(service_name, service_status)

        denied = ['Services', 'Website', 'Panel', 'Billing', 'Authentication', 'APIs', 'IaaS', 
        'DNS/CDN PoP-Sites', 'Support', 'Telephone', 'Ticketing']

        add_IaaS = ['Serverius (Netherlands-Amsterdam)', 'Asiatech', 'Mobinnet']
        add_DNS_CDN_popsite = ['Europe', 'North America', 'Asia', 'Iran']

        with open('config.yml', 'r') as yaml_config:
            context = yaml.load(yaml_config, Loader=yaml.FullLoader)

        cron = context[0]['config']['cron']
        wait = context[0]['config']['wait']

        for srv in row_name:
            current_time = time.time()
            if srv[0].strip() in denied:
                continue
            elif srv[0].strip() in add_IaaS:
                if srv[1].strip() != 'Operational':
                    service_infra_name = 'IaaS - ' + srv[0].strip(),
                    service_infra_status = srv[1].strip()
                    if service_infra_name[0] not in self.list_of_alerts:
                        self.list_of_alerts.extend((str(current_time), service_infra_name[0], service_infra_status))
            elif srv[0].strip() in add_DNS_CDN_popsite:
                if srv[1].strip() != 'Operational':
                    service_infra_name = 'DNS/CDN PoP-Sites - ' + srv[0].strip(),
                    service_infra_status = srv[1].strip()
                    if service_infra_name[0] not in self.list_of_alerts:
                        self.list_of_alerts.extend((str(current_time), service_infra_name[0], service_infra_status))
            else:
                if srv[1].strip() != 'Operational':
                    service_infra_name = srv[0].strip()
                    service_infra_status =  srv[1].strip()
                    if service_infra_name not in self.list_of_alerts:
                        self.list_of_alerts.extend((str(current_time), service_infra_name, service_infra_status))
            #print(self.list_of_alerts)

            new_time = time.time()
            for alt in self.list_of_alerts:
                if re.search('\.', alt):
                    get_time = alt
                    if float(new_time) > float(get_time) + float(wait):
                        get_time = self.list_of_alerts.pop(0)
                        sv_inf_name = self.list_of_alerts.pop(0)
                        sv_inf_status = self.list_of_alerts.pop(0)
                        self.alerting(sv_inf_name, sv_inf_status)
        yield scrapy.Request(response.url, callback=self.parse, dont_filter=True)
        time.sleep(cron)
