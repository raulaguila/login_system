def userEntity(user) -> dict:
    return {
        "id": str(user["_id"]),
        "name": user["name"],
        "username": user["username"],
        "role": user["role"],
        "status": user["status"],
        "photo": user["photo"],
        "email": user["email"],
        # "verified": user["verified"],
        "password": user["password"],
        "created_at": user["created_at"],
        "updated_at": user["updated_at"]
    }


def userResponseEntity(user) -> dict:
    return {
        "id": str(user["_id"]),
        "name": user["name"],
        "username": user["username"],
        "role": user["role"],
        "status": user["status"],
        "photo": user["photo"],
        "email": user["email"],
        "created_at": user["created_at"],
        "updated_at": user["updated_at"]
    }


def embeddedUserResponse(user) -> dict:
    return {
        "id": str(user["_id"]),
        "name": user["name"],
        "username": user["username"],
        # "photo": user["photo"]
    }


def userListEntity(users) -> list:
    return [userEntity(user) for user in users]
