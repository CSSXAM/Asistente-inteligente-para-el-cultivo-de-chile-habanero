from torchvision import transforms

TAMANO_IMAGEN = 224

MEDIA = [0.485, 0.456, 0.406]
DESVIACION = [0.229, 0.224, 0.225]


def obtener_transformaciones_entrenamiento():
    return transforms.Compose([
        transforms.Resize((TAMANO_IMAGEN, TAMANO_IMAGEN)),
        transforms.RandomHorizontalFlip(p=0.5),
        transforms.RandomVerticalFlip(p=0.5),
        transforms.RandomRotation(15),
        transforms.ColorJitter(
            brightness=0.15,
            contrast=0.15,
            saturation=0.10
        ),
        transforms.ToTensor(),
        transforms.Normalize(
            mean=MEDIA,
            std=DESVIACION
        )
    ])


def obtener_transformaciones_evaluacion():
    return transforms.Compose([
        transforms.Resize((TAMANO_IMAGEN, TAMANO_IMAGEN)),
        transforms.ToTensor(),
        transforms.Normalize(
            mean=MEDIA,
            std=DESVIACION
        )
    ])