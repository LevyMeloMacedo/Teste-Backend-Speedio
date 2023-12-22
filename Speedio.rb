require 'nokogiri'
require 'open-uri'
require 'mongo'

client = Mongo::Client.new(['localhost:27017'], :database => 'similarweb')
collection = client[:sites]

def get_info(url)
  response = URI.open(url)
  html = Nokogiri::HTML(response)

  ranking = html.css('div.wa-rank-list.wa-rank-list--md').text
  site = html.css('p.wa-overview__title').text
  category = html.css('p.engagement-list__item-value').text

  avg_visit = html.at('div.engagement-list__item[data-test="avg-visit-duration"]')
  avg_visit_duration = avg_visit.at('p.engagement-list__item-value').text

  pages_per = html.at('div.engagement-list__item[data-test="bounce-rate"]')
  pages_per_visit = pages_per.at('p.engagement-list__item-value').text

  bounce = html.at('div.engagement-list__item[data-test="bounce-rate"]')
  bounce_rate = bounce.at('p.engagement-list__item-value').text

  main_countries = html.css('p.engagement-list__item-value').map(&:text)

  gender_distribution = html.css('ul.wa-demographics__gender-legend').text

  age_distribution = html.css('d.highcharts-679lgvi-234').map(&:text).map(&:to_i)

  data = {
    'ranking' => ranking,
    'site' => site,
    'category' => category,
    'avg_visit_duration' => avg_visit_duration,
    'pages_per_visit' => pages_per_visit,
    'bounce_rate' => bounce_rate,
    'main_countries' => main_countries,
    'gender_distribution' => gender_distribution,
    'age_distribution' => age_distribution
  }

  collection.insert_one(data)

  return data
end

def save_info(url)
  begin
    response = URI.open(url)
  rescue StandardError => e
    puts e
    return 400
  end

  html = Nokogiri::HTML(response)
  data = get_info(url)
  collection.insert_one(data)

  return 201
end

def get_info_by_url(url)
  begin
    data = collection.find('site' => url).first
  rescue Mongo::Error::NoDocuments => e
    puts e
    return 404
  end

  return data
end

def main
  url_base = 'https://www.similarweb.com/top-websites/'
  print 'Site deseja acessar? '
  url = url_base + gets.chomp
  info = get_info(url)
  puts info
end

main if __FILE__ == $PROGRAM_NAME
