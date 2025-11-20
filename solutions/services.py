from rest_framework.exceptions import ValidationError

def validate_allowed_fields(data: dict, allowed_fields: set) -> None:
    """
    data에 allowed_fields 이외의 키가 있으면 400 에러를 던진다.
    """
    incoming_fields = set(data.keys())
    invalid_fields = incoming_fields - allowed_fields

    if invalid_fields:
        raise ValidationError(
            {field: ["이 필드는 수정할 수 없습니다."] for field in invalid_fields}
        )
