from keras.layers import Dense, GlobalAveragePooling2D
from keras.applications.xception import Xception
from keras.models import Model,model_from_json
from keras.applications.mobilenet import preprocess_input
from keras.preprocessing.image import ImageDataGenerator


def create_model_keras(base_model=None, n_class=2, img_width=80, img_height=80):
    if base_model is None:
        base_model = Xception(input_shape=(img_width, img_height, 3), weights='imagenet', include_top=False)

    x = base_model.output
    x = GlobalAveragePooling2D()(x)
    # we add dense layers so that the model can learn more complex functions and classify for better results.
    x = Dense(1024, activation='relu')(x)
    # dense layer 2
    x = Dense(1024, activation='relu')(x)
    # dense layer 3
    x = Dense(512, activation='relu')(x)
    # final layer with softmax activation
    preds = Dense(n_class, activation='softmax')(x)
    #create model
    model = Model(inputs=base_model.input, outputs=preds)
    return model

def save_model(model,model_name):
    # Save model
    model_json = model.to_json()
    with open(model_name + ".json", "w") as json_file:
        json_file.write(model_json)
    model.save_weights(model_name + ".h5")

def train_keras(train_path,test_path,model,num_layers=5,img_width=80, img_height=80,batch_size=30,epochs=10):
    if num_layers== None or num_layers > len(model.layers):
        for layer in model.layers:
            layer.trainable = True
    else:
        for i, layer in enumerate(model.layers[:-num_layers]):
            print(i, layer.name)
    model.compile(optimizer='Adam', loss='categorical_crossentropy', metrics=['accuracy'])

    # Carregando dados de treino
    train_datagen = ImageDataGenerator(preprocessing_function=preprocess_input)  # included in our dependencies
    path_train = train_path
    train_generator = train_datagen.flow_from_directory(path_train,
                                                        target_size=(img_width, img_height),
                                                        color_mode='rgb',
                                                        batch_size=batch_size,
                                                        class_mode='categorical',
                                                        shuffle=True)
    #Carregando dados de test
    test_datagen = ImageDataGenerator(preprocessing_function=preprocess_input)  # included in our dependencies
    path_test = test_path
    validation_generator = test_datagen.flow_from_directory(path_test,
                                                            target_size=(img_width, img_height),
                                                            class_mode='categorical')
    #Copilando o modelo
    step_size_train = train_generator.n // train_generator.batch_size
    model.fit_generator(generator=train_generator,
                        steps_per_epoch=step_size_train,
                        epochs=epochs,
                        validation_data=validation_generator,
                        validation_steps=10)
    return model


from tensorflow.python.client import device_lib
print("Keras:",device_lib.list_local_devices())
print("Keras Ok!")

train_path = '../../data/imagens/RGB/windows/train/'
test_path = '../../data/imagens/RGB/windows/test/'
model = create_model_keras()
model = train_keras(train_path,test_path,model)
save_model(model,'../../data/models/keras_1')
