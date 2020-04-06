# -*- coding: utf-8 -*-
import scrapy


class Covid19StatsSpider(scrapy.Spider):
	name = 'covid19_stats'
	allowed_domains = ['www.worldometers.info/coronavirus']
	start_urls = ['http://www.worldometers.info/coronavirus/']

	def parse(self, response):
		def parse_table_stats(tbody):
			stats = []
			keys = [
				'country',
				'total_cases',
				'new_cases',
				'total_deaths',
				'new_deaths',
				'total_recovered',
				'active_cases',
				'serious_critical',
				'total_cases/1m_population',
				'deaths/1m_population'
			]

			trs = tbody.css('tr')
			for tr in trs:
				tds = tr.css('td')
				values = [td.css('::text').get(default='').strip() for td in tds]

				stats.append({k: v for k, v in zip(keys, values)})

			return stats

		def parse_cases(panel_body):
			div = panel_body.css('.panel_flip')

			first_data = div.css('.panel_front .number-table-main::text').get()

			second_data = {
				'quantity': div.css('.panel_front .number-table::text').get().strip(),
				'percentage': div.css('.panel_front strong::text').get() + '%'
			}

			third_data = {
				'quantity': div.css('div + div > span::text').get().strip(),
				'percentage': div.css('div + div > strong::text').get() + '%'
			}

			return first_data, second_data, third_data

		main_table = response.css('#main_table_countries_today')[0]

		tbody_countries = main_table.css('tbody')[0]
		countries_stats = parse_table_stats(tbody_countries)

		tbody_total = main_table.css('tbody')[1]
		total_stats = parse_table_stats(tbody_total)[0]
		del total_stats['country']

		active_cases = parse_cases(response.css('.panel-body')[0])
		active_cases = {
			'current_infected_patients': active_cases[0],
			'in_mild_condition': active_cases[1],
			'serious_or_critical': active_cases[2]
		}

		closed_cases = parse_cases(response.css('.panel-body')[1])
		closed_cases = {
			'cases_which_had_an_outcome': closed_cases[0],
			'recovered/discharged': closed_cases[1],
			'deaths': closed_cases[2]
		}

		yield {
			'countries_stats': countries_stats,
			'total_stats': total_stats,
			'active_cases': active_cases,
			'closed_cases': closed_cases
		}
