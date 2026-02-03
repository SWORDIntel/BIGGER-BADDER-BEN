#!/usr/bin/env python3
"""
Pluggable Renderer Interface for Atomic Clock Display

Defines the interface that all renderers must implement.
"""

from abc import ABC, abstractmethod
from typing import Dict, Optional, Tuple
from datetime import datetime


class ClockRenderer(ABC):
    """Abstract base class for clock renderers."""
    
    @abstractmethod
    def initialize(self, width: int, height: int) -> bool:
        """
        Initialize the renderer.
        
        Args:
            width: Display width
            height: Display height
            
        Returns:
            True if initialization successful, False otherwise
        """
        pass
    
    @abstractmethod
    def update_display(self, current_time: datetime, corner_times: Dict[str, Dict]) -> None:
        """
        Update the display with current time data.
        
        Args:
            current_time: Current UTC time
            corner_times: Dictionary mapping corner positions to time info
        """
        pass
    
    @abstractmethod
    def update_size(self, width: int, height: int) -> None:
        """
        Update display size.
        
        Args:
            width: New display width
            height: New display height
        """
        pass
    
    @abstractmethod
    def cleanup(self) -> None:
        """Cleanup resources on exit."""
        pass
    
    @abstractmethod
    def handle_keypress(self, key: str) -> bool:
        """
        Handle keyboard input.
        
        Args:
            key: Key character pressed
            
        Returns:
            True if key was handled, False if not handled
        """
        pass
    
    @abstractmethod
    def show_help(self) -> None:
        """Display help overlay."""
        pass
    
    @abstractmethod
    def hide_help(self) -> None:
        """Hide help overlay."""
        pass
    
    @abstractmethod
    def get_size(self) -> Tuple[int, int]:
        """
        Get current display size.
        
        Returns:
            Tuple of (width, height)
        """
        pass


class RendererFactory:
    """Factory for creating renderer instances."""
    
    _renderers = {}
    
    @classmethod
    def register(cls, name: str, renderer_class):
        """Register a renderer class."""
        cls._renderers[name] = renderer_class
    
    @classmethod
    def create(cls, renderer_type: str, **kwargs) -> ClockRenderer:
        """
        Create a renderer instance.
        
        Args:
            renderer_type: Type of renderer to create
            **kwargs: Additional arguments for renderer
            
        Returns:
            Renderer instance
            
        Raises:
            ValueError: If renderer type not found
        """
        if renderer_type not in cls._renderers:
            available = ', '.join(cls._renderers.keys())
            raise ValueError(f"Unknown renderer type: {renderer_type}. Available: {available}")
        
        renderer_class = cls._renderers[renderer_type]
        return renderer_class(**kwargs)
    
    @classmethod
    def list_renderers(cls) -> list:
        """List available renderer types."""
        return list(cls._renderers.keys())


def register_renderer(name: str):
    """Decorator to register a renderer class."""
    def decorator(cls):
        RendererFactory.register(name, cls)
        return cls
    return decorator
