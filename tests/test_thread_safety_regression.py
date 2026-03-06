import ast
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _parse_module(file_name: str) -> ast.Module:
    source = (PROJECT_ROOT / file_name).read_text(encoding="utf-8")
    return ast.parse(source)


def _get_class(module: ast.Module, class_name: str) -> ast.ClassDef:
    for node in module.body:
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            return node
    raise AssertionError(f"Class {class_name} not found")


def _get_method(class_node: ast.ClassDef, method_name: str) -> ast.FunctionDef | ast.AsyncFunctionDef:
    for node in class_node.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == method_name:
            return node
    raise AssertionError(f"Method {method_name} not found in class {class_node.name}")


def _has_call_to_attr(node: ast.AST, attr_name: str) -> bool:
    for child in ast.walk(node):
        if isinstance(child, ast.Call) and isinstance(child.func, ast.Attribute):
            if child.func.attr == attr_name:
                return True
    return False


def _has_decorator(method: ast.FunctionDef | ast.AsyncFunctionDef, decorator_name: str) -> bool:
    for decorator in method.decorator_list:
        if isinstance(decorator, ast.Name) and decorator.id == decorator_name:
            return True
        if isinstance(decorator, ast.Attribute) and decorator.attr == decorator_name:
            return True
    return False


def test_light_message_callback_is_loop_safe():
    module = _parse_module("light.py")
    entity = _get_class(module, "SphaLight")

    message_received = _get_method(entity, "_message_received")

    assert isinstance(message_received, ast.FunctionDef)
    assert _has_decorator(message_received, "callback")
    assert _has_call_to_attr(message_received, "async_write_ha_state")


def test_cover_entity_commands_are_async_and_write_state_on_loop():
    module = _parse_module("cover.py")
    entity = _get_class(module, "SphaCover")

    for method_name in ("async_open_cover", "async_close_cover", "async_stop_cover"):
        method = _get_method(entity, method_name)
        assert isinstance(method, ast.AsyncFunctionDef)
        assert _has_call_to_attr(method, "async_write_ha_state")

    for forbidden_name in ("open_cover", "close_cover", "stop_cover"):
        with_forbidden_name = [
            node
            for node in entity.body
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            and node.name == forbidden_name
        ]
        assert not with_forbidden_name


def test_cover_relay_uses_async_publish():
    module = _parse_module("cover.py")
    relay = _get_class(module, "Relay")

    for method_name in ("async_turn_on", "async_turn_off"):
        method = _get_method(relay, method_name)
        assert isinstance(method, ast.AsyncFunctionDef)
        assert _has_call_to_attr(method, "async_publish")
