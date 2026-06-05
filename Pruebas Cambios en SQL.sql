CREATE TABLE clientes (
  id INT PRIMARY KEY,
  nombre TEXT,
  email TEXT
);

SELECT *
FROM clientes;

INSERT INTO clientes
SELECT 3, 'Maria', 'prueba3@gmail.com';

UPDATE clientes SET nombre = 'Pedro'
WHERE id = 2;

DELETE FROM clientes
WHERE id = 2;
