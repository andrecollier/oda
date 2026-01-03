"""Kassal.app API client."""

import httpx
from typing import Any

from .models import Product, ProductSearch, ProductSearchParams


class KassalClient:
    """Client for interacting with Kassal.app API."""

    def __init__(self, api_key: str, base_url: str = "https://kassal.app/api/v1"):
        """Initialize Kassal API client.

        Args:
            api_key: Bearer token for authentication
            base_url: Base URL for API (default: https://kassal.app/api/v1)
        """
        self.base_url = base_url.rstrip("/")
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Accept": "application/json",
        }
        self.client = httpx.AsyncClient(headers=self.headers, timeout=30.0)

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()

    async def __aenter__(self):
        """Context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        await self.close()

    async def search_products(self, params: ProductSearchParams) -> ProductSearch:
        """Search for products.

        Args:
            params: Search parameters

        Returns:
            ProductSearch object with results

        Raises:
            httpx.HTTPError: If the request fails
        """
        query_params = {}
        for k, v in params.model_dump(exclude_none=True).items():
            if v is not None:
                # Convert booleans to integers for API compatibility
                if isinstance(v, bool):
                    query_params[k] = int(v)
                else:
                    query_params[k] = v

        # Handle list parameters
        if params.excl_allergens:
            query_params["excl_allergens"] = ",".join(params.excl_allergens)
        if params.has_labels:
            query_params["has_labels"] = ",".join(params.has_labels)

        response = await self.client.get(f"{self.base_url}/products", params=query_params)
        response.raise_for_status()
        return ProductSearch(**response.json())

    async def get_product(self, product_id: int) -> Product:
        """Get detailed product information by ID.

        Args:
            product_id: Product ID

        Returns:
            Product object

        Raises:
            httpx.HTTPError: If the request fails
        """
        response = await self.client.get(f"{self.base_url}/products/id/{product_id}")
        response.raise_for_status()
        return Product(**response.json()["data"])

    async def get_product_by_ean(self, ean: str) -> list[Product]:
        """Get product by EAN/barcode with cross-store comparison.

        Args:
            ean: EAN barcode

        Returns:
            List of products (same product from different stores)

        Raises:
            httpx.HTTPError: If the request fails
        """
        response = await self.client.get(f"{self.base_url}/products/ean/{ean}")
        response.raise_for_status()
        data = response.json()
        return [Product(**p) for p in data.get("data", [])]

    async def find_deals(
        self, category: str | None = None, min_discount: float = 0.1
    ) -> list[Product]:
        """Find products currently on sale.

        Args:
            category: Optional category filter
            min_discount: Minimum discount threshold (default 10%)

        Returns:
            List of products on sale
        """
        params = ProductSearchParams(
            store="ODA_NO",
            category=category,
            sort="price_desc",
            size=100,
        )

        results = await self.search_products(params)
        deals = [p for p in results.data if p.is_on_sale]
        return deals

    async def find_high_protein_products(
        self, search: str | None = None, min_protein: float = 15.0
    ) -> list[Product]:
        """Find high-protein products.

        Args:
            search: Optional search term
            min_protein: Minimum protein per 100g (default: 15g)

        Returns:
            List of high-protein products
        """
        params = ProductSearchParams(
            store="ODA_NO",
            search=search,
            size=100,
        )

        results = await self.search_products(params)
        high_protein = [
            p
            for p in results.data
            if p.protein_per_100g and p.protein_per_100g >= min_protein
        ]
        return high_protein

    async def search_by_ingredients(self, ingredients: list[str]) -> dict[str, list[Product]]:
        """Search for products matching a list of ingredients.

        Args:
            ingredients: List of ingredient names

        Returns:
            Dictionary mapping ingredient names to matching products
        """
        results = {}
        for ingredient in ingredients:
            params = ProductSearchParams(
                store="ODA_NO",
                search=ingredient,
                size=10,
                sort="price_asc",
            )
            search_result = await self.search_products(params)
            results[ingredient] = search_result.data
        return results
