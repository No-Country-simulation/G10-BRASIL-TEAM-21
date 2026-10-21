"""Placeholder do treino do classificador local.

Uso previsto (semana 2): python -m app.infra.classifiers.train
Saída: backend/data/classifiers/modelo-v1.pkl

Dataset sintético esperado em backend/data/classifiers/dataset.csv com
colunas `texto,dominio` e >= 200 exemplos por 4 a 6 domínios.
"""

from pathlib import Path


def main() -> None:
    print(
        "Treino ainda nao implementado. "
        "Adicione backend/data/classifiers/dataset.csv "
        "e implemente TF-IDF + LogisticRegression."
    )
    data_dir = Path(__file__).resolve().parents[2] / "data" / "classifiers"
    data_dir.mkdir(parents=True, exist_ok=True)
    print(f"Diretorio de dados: {data_dir}")


if __name__ == "__main__":
    main()
