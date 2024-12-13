# Módulo 10 - Listagem de Vídeos

# Aula 10.1 - Introdução

- [Diagrama C4](../notes/resources/diagrama-c4.png)
- [Diagrama de sequência](../notes/resources/saveVideoUseCase.png)
- [Video Domain Object - Catalog Admin](https://github.com/gcrsaldanha/codeflix-catalog-admin/blob/main/src/core/video/domain/video.py)
- [Video Value Objects](https://github.com/gcrsaldanha/codeflix-catalog-admin/blob/main/src/core/video/domain/value_objects.py)
- API de Video (versão simplificada)
    - title
    - launch_year
    - rating
    - categories
    - genres
    - cast_members
    - banner
```json
{
  "data": [
    {
      "id": "4ed7573d-b993-11ef-b0cc-0242ac120003",
      "title": "The Godfather",
      "launch_year": 1972,
      "rating": "AGE_18",
      "categories": [
        "142f2b4b-1b7b-4f3b-8eab-3f2f2b4b1b7b"
      ],
      "genres": [
        "442f2b4b-1b7b-4f3b-8eab-3f2f2b4b1b7b"
      ],
      "cast_members": [
        "242f2b4b-1b7b-4f3b-8eab-3f2f2b4b1b7b",
        "342f2b4b-1b7b-4f3b-8eab-3f2f2b4b1b7b"
      ],
      "banner_url": "https://banner.com/the-godfather",
      "created_at": "2024-12-13T20:46:20Z",
      "updated_at": "2024-12-13T20:46:20Z",
      "is_active": true
    }

  ],
  "meta": {
    "page": 1,
    "per_page": 5,
    "sort": "title",
    "direction": "asc"
  }
}
```


# Aula 10.2 - ListVideo

- `Video` (versão reduzida) e apenas o `Rating` de ValueObject.
- `VideoRepository`
- `ListVideo` UseCase
- `ElasticsearchVideoRepository`
- `VideoRouter`
