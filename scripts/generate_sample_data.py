import csv, random, datetime, pathlib
random.seed(42)
data_dir = pathlib.Path('data')
data_dir.mkdir(exist_ok=True)
hosts = []
for i in range(1, 501):
    hosts.append({'id': i, 'name': 'Host ' + str(i), 'is_superhost': random.choice(['t','f']), 'created_at': '2015-01-01', 'updated_at': '2024-01-01'})
with open(data_dir / 'hosts.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=['id','name','is_superhost','created_at','updated_at'])
    w.writeheader()
    w.writerows(hosts)
print('hosts.csv OK - ' + str(len(hosts)) + ' rows')
nb = ['Mitte','Prenzlauer Berg','Kreuzberg','Friedrichshain','Neukoelln','Charlottenburg','Schoeneberg','Pankow']
listings = []
for i in range(1, 1001):
    listings.append({'id': i, 'host_id': random.randint(1,500), 'neighbourhood': random.choice(nb), 'room_type': random.choice(['Entire home/apt','Private room','Shared room']), 'price': str(round(random.uniform(30,300),2)), 'minimum_nights': random.randint(1,5), 'number_of_reviews': random.randint(0,200), 'review_scores_rating': round(random.uniform(3.5,5.0),2), 'beds': random.randint(1,6), 'amenities': 'wifi,kitchen', 'latitude': round(52.5+random.uniform(-0.1,0.1),6), 'longitude': round(13.4+random.uniform(-0.2,0.2),6)})
with open(data_dir / 'listings.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=['id','host_id','neighbourhood','room_type','price','minimum_nights','number_of_reviews','review_scores_rating','beds','amenities','latitude','longitude'])
    w.writeheader()
    w.writerows(listings)
print('listings.csv OK - ' + str(len(listings)) + ' rows')
reviews = []
for i in range(1, 5001):
    dt = datetime.date(2023,1,1) + datetime.timedelta(days=random.randint(0,700))
    reviews.append({'listing_id': random.randint(1,1000), 'id': i, 'date': str(dt), 'reviewer_id': random.randint(1000,9999), 'reviewer_name': 'Reviewer' + str(i), 'comments': 'Great stay!'})
with open(data_dir / 'reviews.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=['listing_id','id','date','reviewer_id','reviewer_name','comments'])
    w.writeheader()
    w.writerows(reviews)
print('reviews.csv OK - ' + str(len(reviews)) + ' rows')
