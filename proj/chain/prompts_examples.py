# This will serve as a hub of example prompts the chain should be able to handle...
# Can be used to improve model performance, as few shot examples when querying the database.


examples = [
    {
        "input": "Are any of my medicines going out of date?",
        "query": "SELECT `p`.`product_name`, `pe`.`expiry_date`  FROM `products` AS `p` JOIN `product_expiry` AS `pe` ON `p`.`id` = `pe`.`id` WHERE `p`.`category` = 'Medicine' AND `pe`.`expiry_date` > CURDATE() ORDER BY `pe`.`expiry_date` ASC LIMIT 3;",
    },
    {
        "input": "Are any of my products going out of date?",
        "query": "SELECT `products`.`product_name`, `product_expiry`.`expiry_date`  FROM `products`  JOIN `product_expiry` ON `products`.`id` = `product_expiry`.`id`  WHERE `product_expiry`.`expiry_date` < CURDATE() + INTERVAL 30 DAY  LIMIT 3;"
    },
    {
        "input": "Show me all medications in the 'Prescription' category",
        "query": "SELECT  `products`.`product_name`, `products`.`supplier`, `products`.`category` FROM `products` WHERE `products`.`category` = 'Prescription';",
    },
    {
        "input": "What medication do I need to reorder",
        "query": "SELECT `product_name`, `stock_count` FROM `products` WHERE `category` = 'Medicine' AND `stock_count` < 20 LIMIT 5",
    },
    {
        "input": "What stock is running low?",
        "query": "SELECT `product_name`, `stock_count` FROM `products` WHERE `stock_count` < 20 ORDER BY `stock_count` ASC LIMIT 5;",
    },
    {
        "input": "Show me current stock levels (Show tables)",
        "query": "SELECT `id`, `product_name`, `stock_count` FROM `products` LIMIT 5;",
    },
    {
        "input": "Show me the products with the highest stock.",
        "query": "SELECT `product_name`, `stock_count`  FROM `products`  ORDER BY `stock_count` DESC  LIMIT 5;"
    },
    {
        "input": "Add new medication 'Aspirin' to inventory with stock level 100, category 'General'",
        "query": "INSERT INTO `products` (`product_name`, `supplier`, `category`, `stock_count`, `cost`) VALUES ('Aspirin', NULL, 'General', 100, NULL)",
    },
    {
        "input": "List all products expiring in the next month",
        "query": "SELECT `id`, `expiry_date`, `quantity` FROM `product_expiry` WHERE `expiry_date` BETWEEN CURDATE() AND LAST_DAY(CURDATE() + INTERVAL 1 MONTH) LIMIT 3;",
    },
    {
        "input": "Create new order for Paracetamol, quantity 500",
        "query": "INSERT INTO `orders` (`product_id`, `order_date`, `quantity`) SELECT `id`, CURDATE(), 500 FROM `products` WHERE `product_name` = 'Paracetamol'",
    },
    {
        "input": "Create new order for Carrington Antifungal, quantity 500",
        "query": "INSERT INTO `orders` (`product_id`, `order_date`, `quantity`) VALUES ((SELECT `id` FROM `products` WHERE `product_name` = 'Carrington Antifungal'), CURDATE(), 500);",
    },
    {
        "input": "Change category of Aspirin from 'General' to 'OTC'",
        "query": "UPDATE `products` SET `category` = 'OTC' WHERE `product_name` = 'Aspirin';"
    },
    {
        "input": "Filter inventory by expiry date descending order",
        "query": "SELECT `id`, `expiry_date`, `quantity` FROM `product_expiry` ORDER BY `expiry_date` DESC LIMIT 3;",
    },
    {
        "input": "What is the date of my order for midodrine hydrochloride?",
        "query": "SELECT `orders`.`order_date`  FROM `orders`  JOIN `products` ON `orders`.`product_id` = `products`.`id`  WHERE `products`.`product_name` = 'Midodrine Hydrochloride'  LIMIT 3;",
    },
    {
        "input": "What is the order date for my ALCOHOL?",
        "query": "SELECT `orders`.`order_date`  FROM `orders`  JOIN `products` ON `orders`.`product_id` = `products`.`id`  WHERE `products`.`product_name` = 'ALCOHOL'  LIMIT 3;",
    },
    {
        "input": "Register new prescription medication in system named 'GPT Lover 300mg with quantity 200",
        "query": "INSERT INTO `products` (`product_name`, `supplier`, `category`, `stock_count`, `cost`) VALUES ('GPT Lover 300mg', NULL, 'Medicine', 200, 0.00);",
    },
    {
        "input": "Do any of my inventory look like there is a pricing error?",
        "query": "SELECT `product_name`, `cost` FROM `products` WHERE `cost` = 0 OR `cost` < 0.50 ORDER BY `cost` DESC LIMIT 5;",
    },
    {
        "input": "Update stock level for Daytime Nitetime to 200 units",
        "query": "UPDATE `products` SET `stock_count` = 200 WHERE `product_name` = 'Daytime Nitetime';",
    },
    {
        "input": "Show all products with stock below minimum threshold of 25 units",
        "query": "SELECT `product_name`, `stock_count` FROM `products` WHERE `stock_count` < 25 ORDER BY `stock_count` DESC LIMIT 5;",
    },
    {
        "input": "What is the average stock level of all products?",
        "query": "SELECT AVG(`stock_count`) AS average_stock_level FROM `products`;",
    },
    {
        "input": "Delete order #87 from system",
        "query": "DELETE FROM `orders` WHERE `order_id` = 87;",
    },
    {
        "input": "What is the top category of products?",
        "query": "SELECT `category`, COUNT(*) AS category_count FROM `products` GROUP BY `category` ORDER BY category_count DESC LIMIT 1;",
    },
    {
        "input": "What is the least popular category of products?",
        "query": "SELECT `category`, COUNT(*) AS category_count FROM `products` GROUP BY `category` ORDER BY category_count ASC LIMIT 1;",
    },
    {
        "input": "What is the most popular product based on my orders?",
        "query": "SELECT `p`.`product_name`, SUM(`o`.`quantity`) AS total_quantity FROM `orders` AS `o` JOIN `products` AS `p` ON `o`.`product_id` = `p`.`id` GROUP BY `p`.`product_name` ORDER BY total_quantity DESC LIMIT 1;",
    },
    {
        "input": "what was the average number of orders in the last 30 days",
        "query": "SELECT AVG(`quantity`) AS average_orders FROM `orders` WHERE `order_date` >= CURDATE() - INTERVAL 30 DAY;"
    }

]


s = [

    {
        "input": "What is the expected delivery time for my order of paracetamol?",
        "query": "",
    },
    # Read Operations

    {
        "input": "Display all orders with expected delivery this week",
        "query": "",
    },
    # Delete Operations
    {
        "input": "Remove expired medication from inventory",
        "query": "",
    },

    {
        "input": "Cancel pending order for Ibuprofen",
        "query": "",
    },
]

# Prompts to do with CRUD operations on the inventory.
# Allow the ordering of items online.
