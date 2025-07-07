
# main.py
from mcp.server.fastmcp import FastMCP
import uvicorn
from db import get_db_connection

mcp = FastMCP("ecommerce-sqlite")

@mcp.tool()
def add_product(name: str, price: float, stock: int = 0) -> dict:
    """
    Add a new product to the eCommerce catalog.

    Parameters:
    - name: The name of the product (e.g., "Wireless Mouse").
    - price: The selling price of the product in decimal format (e.g., 29.99).
    - stock: The initial quantity of the product available in inventory. Defaults to 0 if not specified.

    Returns:
    - A success message with the assigned product ID if added successfully.
    - An error message if the insertion fails.

    Example:
    add_product(name="Bluetooth Speaker", price=49.99, stock=10)
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if product name already exists (case-insensitive)
    cursor.execute("SELECT id, name FROM products WHERE LOWER(name) = LOWER(?)", (name,))
    existing_product = cursor.fetchone()
    
    if existing_product:
        conn.close()
        return {
            "status": "error", 
            "message": f"Product with name '{name}' already exists (ID: {existing_product[0]})"
        }
    
    # Add the product if name doesn't exist
    cursor.execute(
        "INSERT INTO products (name, price, stock) VALUES (?, ?, ?)",
        (name, price, stock)
    )
    conn.commit()
    product_id = cursor.lastrowid
    conn.close()
    return {"status": "success", "product_id": product_id}



@mcp.tool()
def list_products() -> list[dict]:
    """
    List all products currently available in the catalog.

    This tool returns all available product records with their ID, name, price, and stock levels.
    Useful for showing users what can be purchased, managed, or updated.

    Returns:
    - A list of dictionaries, each with:
        - id (int)
        - name (str)
        - price (float)
        - stock (int)

    Example call:
    list_products()
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, price, stock FROM products")
    products = cursor.fetchall()
    conn.close()
    return [{"id": p[0], "name": p[1], "price": p[2], "stock": p[3]} for p in products]


@mcp.tool()
def delete_product(product_id: int = None, name: str = None, confirm_multiple: bool = False) -> dict:
    """
    Delete a product from the catalog by ID or name.

    Use this tool to remove a product from the database. 
    If deleting by name and multiple matches exist, set `confirm_multiple=True` to confirm bulk deletion.

    Parameters:
    - product_id (int, optional): Unique product ID to delete.
    - name (str, optional): Product name (case-insensitive). Deletes all products with matching name unless `confirm_multiple=False`.
    - confirm_multiple (bool): Set to True to delete all products with the specified name.

    Returns:
    - dict with:
        - status: "success", "error", or "warning"
        - deleted_count
        - product_name or message
        - matching_products (if warning)
        - suggestion (if confirmation needed)

    Examples:
    delete_product(product_id=5)
    delete_product(name="USB Cable", confirm_multiple=True)
    """
    if not product_id and not name:
        return {"status": "error", "message": "Please provide either product_id or name."}
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if product_id:
        # Delete by ID (specific product)
        cursor.execute("SELECT name FROM products WHERE id = ?", (product_id,))
        product = cursor.fetchone()
        if not product:
            conn.close()
            return {"status": "error", "message": f"No product found with ID {product_id}."}
        
        cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
        conn.commit()
        conn.close()
        return {"status": "success", "deleted_count": 1, "product_name": product[0]}
    
    elif name:
        # Check how many products match the name (case-insensitive)
        cursor.execute("SELECT COUNT(*) FROM products WHERE LOWER(name) = LOWER(?)", (name,))
        count = cursor.fetchone()[0]
        
        if count == 0:
            conn.close()
            return {"status": "error", "message": f"No product found with name '{name}'."}
        
        # If multiple products match and user hasn't confirmed, warn them
        if count > 1 and not confirm_multiple:
            cursor.execute("SELECT id, name, price FROM products WHERE LOWER(name) = LOWER(?)", (name,))
            matching_products = cursor.fetchall()
            conn.close()
            return {
                "status": "warning", 
                "message": f"Found {count} products with name '{name}'. This will delete ALL of them.",
                "matching_products": [{"id": p[0], "name": p[1], "price": p[2]} for p in matching_products],
                "suggestion": "Use product_id for specific deletion, or call again with confirm_multiple=True to delete all."
            }
        
        # Proceed with deletion (case-insensitive)
        cursor.execute("DELETE FROM products WHERE LOWER(name) = LOWER(?)", (name,))
        conn.commit()
        deleted = cursor.rowcount
        conn.close()
        
        return {
            "status": "success", 
            "deleted_count": deleted,
            "message": f"Deleted {deleted} product(s) with name '{name}'."
        }


@mcp.tool()
def search_products_by_name(partial_name: str) -> list[dict]:
    """
    Search for products by partial or full name match.

    Use this tool when the user wants to find a product but may not remember the full name.
    It performs a case-insensitive search and returns all matching products.

    Parameters:
    - partial_name (str): A part or full product name to search for.
                        Examples: "mouse", "USB", "monitor", "wireless"

    Returns:
    - A list of matching products, each with:
        - id (int)
        - name (str)
        - price (float)
        - stock (int)

    Examples:
    search_products_by_name(partial_name="mouse")
    search_products_by_name(partial_name="wireless")
    search_products_by_name(partial_name="speaker")

    Notes:
    - If no products match, an empty list is returned.
    - Ideal for helping users discover product IDs before updating, deleting, or inspecting stock levels.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, name, price, stock FROM products WHERE LOWER(name) LIKE LOWER(?)",
        (f"%{partial_name}%",)
    )
    results = cursor.fetchall()
    conn.close()

    return [
        {"id": row[0], "name": row[1], "price": row[2], "stock": row[3]}
        for row in results
    ]

@mcp.tool()
def update_product_stock(product_id: int, new_stock: int) -> dict:
    """
    Update the stock quantity of a product.

    Use this to manually update the stock count of an existing product.

    Parameters:
    - product_id (int): Unique identifier of the product.
    - new_stock (int): New inventory count (0 or more). Example: 50

    Returns:
    - dict with:
        - status: "success" or "error"
        - product_id
        - new_stock

    Example:
    update_product_stock(product_id=3, new_stock=100)
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM products WHERE id = ?", (product_id,))
    product = cursor.fetchone()
    if not product:
        conn.close()
        return {"status": "error", "message": f"No product found with ID {product_id}"}

    cursor.execute("UPDATE products SET stock = ? WHERE id = ?", (new_stock, product_id))
    conn.commit()
    conn.close()
    return {"status": "success", "product_id": product_id, "new_stock": new_stock}



@mcp.tool()
def update_product_price(product_id: int, new_price: float) -> dict:
    """
    Update the price of a product.

    Use this tool to change the selling price of a product, for discounts, pricing updates, or corrections.

    Parameters:
    - product_id (int): Unique identifier of the product.
    - new_price (float): New product price (USD). Example: 34.95

    Returns:
    - dict with:
        - status: "success" or "error"
        - product_id
        - new_price

    Example:
    update_product_price(product_id=3, new_price=79.99)
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM products WHERE id = ?", (product_id,))
    product = cursor.fetchone()
    if not product:
        conn.close()
        return {"status": "error", "message": f"No product found with ID {product_id}"}

    cursor.execute("UPDATE products SET price = ? WHERE id = ?", (new_price, product_id))
    conn.commit()
    conn.close()
    return {"status": "success", "product_id": product_id, "new_price": new_price}


if __name__ == "__main__":
    mcp.run(transport="stdio")
