db.createcollection("tickets");
db.tickets.createIndex({"created_at": -1});
print("Tickets collection and index created.");