"""
The Central Dogma — DNA -> RNA -> protein

The flow of genetic information in every living cell. DNA is transcribed into
messenger RNA, which the ribosome translates codon by codon into a protein. This
module implements that pipeline — transcription, the genetic code, the reverse
complement of the antisense strand, and GC content — turning a gene into the
amino-acid chain it encodes.
"""

from __future__ import annotations

CODON_TABLE = {
    "UUU": "F", "UUC": "F", "UUA": "L", "UUG": "L", "CUU": "L", "CUC": "L",
    "CUA": "L", "CUG": "L", "AUU": "I", "AUC": "I", "AUA": "I", "AUG": "M",
    "GUU": "V", "GUC": "V", "GUA": "V", "GUG": "V", "UCU": "S", "UCC": "S",
    "UCA": "S", "UCG": "S", "CCU": "P", "CCC": "P", "CCA": "P", "CCG": "P",
    "ACU": "T", "ACC": "T", "ACA": "T", "ACG": "T", "GCU": "A", "GCC": "A",
    "GCA": "A", "GCG": "A", "UAU": "Y", "UAC": "Y", "UAA": "*", "UAG": "*",
    "CAU": "H", "CAC": "H", "CAA": "Q", "CAG": "Q", "AAU": "N", "AAC": "N",
    "AAA": "K", "AAG": "K", "GAU": "D", "GAC": "D", "GAA": "E", "GAG": "E",
    "UGU": "C", "UGC": "C", "UGA": "*", "UGG": "W", "CGU": "R", "CGC": "R",
    "CGA": "R", "CGG": "R", "AGU": "S", "AGC": "S", "AGA": "R", "AGG": "R",
    "GGU": "G", "GGC": "G", "GGA": "G", "GGG": "G",
}


def transcribe(dna: str) -> str:
    """DNA coding strand -> messenger RNA."""
    return dna.replace("T", "U")


def reverse_complement(dna: str) -> str:
    complement = {"A": "T", "T": "A", "C": "G", "G": "C"}
    return "".join(complement[b] for b in reversed(dna))


def gc_content(dna: str) -> float:
    return (dna.count("G") + dna.count("C")) / len(dna)


def translate(mrna: str) -> str:
    """Translate codons into amino acids, stopping at a stop codon."""
    protein = []
    for i in range(0, len(mrna) - 2, 3):
        amino = CODON_TABLE[mrna[i:i + 3]]
        if amino == "*":
            break
        protein.append(amino)
    return "".join(protein)


if __name__ == "__main__":
    gene = "ATGGCTTGCGGAGTTAAGTAA"
    print(f"Gene (DNA): {gene}\n")
    print(f"  GC content        : {gc_content(gene):.1%}")
    print(f"  reverse complement: {reverse_complement(gene)}")

    mrna = transcribe(gene)
    print(f"  mRNA              : {mrna}")

    protein = translate(mrna)
    print(f"  protein           : {protein}")
    print(f"\n  Codons: " + " ".join(mrna[i:i + 3] for i in range(0, len(mrna), 3)))
    print("  AUG starts translation (Met); UAA/UAG/UGA stop it.")
