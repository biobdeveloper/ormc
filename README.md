# ORMCombine


[![License]][LICENSE.md]

Code converter between python ORMs.
* django to sqlalchemy
* sqlalchemy to django

The way to help rewrite python microservice with another ORM framework.

**Currently supports only database schema declaration converter.** 

Now we are searching for the best way to convert orm requests and orm-based microservices entirely

_This is not runtime-extension to extend you models on-the-fly! This is code generator!_


# Run
You need to put your original file with models frequently named `models.py` in root ormcombine's directory and run


```python ormcombine.py -i models.py --to sa -o sa_models.py```
* `sa` - SqlAlchemy
* `django` - Django ORM

<div align="center">
<h1>ORM COMBINE</h1>
<img src="https://i.imgur.com/KneR2QJ.png" width="1200" height="500">



</div>

# About
Supported ORM frameworks:

| ORM        | Support     |
|------------|-------------|
| SqlAlchemy | ✅           |
| Django ORM | ✅           |
| Tortoise   | coming soon |

SQL Types support

| Type     | Support |
|----------|---------|
| CHAR     | ✅       |
| INTEGER  | ✅       |
| BOOLEAN  | ✅       |
| BINARY   | ✅       |
| DATE     | ✅       |
| DATETIME | ✅       |
| DECIMAL  | ✅       |

SQL Features support

| Feature       | Support     |
|---------------|-------------|
| Primary key   | ✅           |
| Auto now time | ✅           |
| Foreign keys  | ✅           |
| One to one    | coming soon |
| Many to many  | coming soon |


# Warning!
There is no any sandbox mode to run this application safely, so when you combine your `models.py` file,
any code inside will be executed. Be careful!

# Install
```bash
git clone https://github.com/biobdeveloper/ormc
cd ormc/
python3 -m venv venv
source venv/bin/activate
```

[License]: https://img.shields.io/github/license/biobdeveloper/ormc
[LICENSE.md]: LICENSE.md