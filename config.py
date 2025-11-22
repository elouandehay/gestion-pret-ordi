class Config:
    #base de données SQLite simple dans le même dossier que le projet
    SQLALCHEMY_DATABASE_URI = "sqlite:///database.db"
    #clé secrète pour flask
    SECRET_KEY = "AAAAAAAAABBBBBBBBBB"