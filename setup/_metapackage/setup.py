import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo8-addons-oca-connector-sage",
    description="Meta package for oca-connector-sage Odoo addons",
    version=version,
    install_requires=[
        'odoo8-addon-exportsage50',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 8.0',
    ]
)
