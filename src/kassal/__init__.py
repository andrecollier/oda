"""Kassal.app API integration for product search and price comparison."""

from .client import KassalClient
from .models import Product, ProductSearch, ProductSearchParams, Store

__all__ = ["KassalClient", "Product", "ProductSearch", "ProductSearchParams", "Store"]
