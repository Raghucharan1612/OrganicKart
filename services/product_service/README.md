CREATE DATABASE organickart_product_db;

CREATE USER 'organickart_product_user'@'localhost'
IDENTIFIED BY 'organickart_product_pass';

GRANT ALL PRIVILEGES
ON organickart_product_db.*
TO 'organickart_product_user'@'localhost';

FLUSH PRIVILEGES;

