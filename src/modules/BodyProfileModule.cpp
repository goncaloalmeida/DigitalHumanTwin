#include "BodyProfileModule.h"

#include <QComboBox>
#include <QGroupBox>
#include <QLabel>
#include <QObject>
#include <QVBoxLayout>
#include <QWidget>

BodyProfileModule::BodyProfileModule() = default;

QString BodyProfileModule::id() const {
    return "body-profile";
}

QString BodyProfileModule::displayName() const {
    return "Body Profile";
}

QWidget* BodyProfileModule::view() {
    if (m_root == nullptr) {
        buildView();
    }

    return m_root;
}

void BodyProfileModule::initialize() {
    view();
    updateDescription(0);
}

void BodyProfileModule::buildView() {
    m_root = new QWidget();

    auto* layout = new QVBoxLayout(m_root);
    auto* intro = new QLabel("Simple sample module for choosing the base body profile.", m_root);
    intro->setWordWrap(true);

    auto* selectionBox = new QGroupBox("Body type", m_root);
    auto* selectionLayout = new QVBoxLayout(selectionBox);

    m_bodyType = new QComboBox(selectionBox);
    m_bodyType->addItems({"Male", "Female", "Neutral"});

    m_description = new QLabel(selectionBox);
    m_description->setWordWrap(true);

    selectionLayout->addWidget(m_bodyType);
    selectionLayout->addWidget(m_description);

    layout->addWidget(intro);
    layout->addWidget(selectionBox);
    layout->addStretch();

    QObject::connect(m_bodyType, qOverload<int>(&QComboBox::currentIndexChanged), m_root, [this](int index) {
        updateDescription(index);
    });
}

void BodyProfileModule::updateDescription(int index) {
    if (m_description == nullptr) {
        return;
    }

    switch (index) {
    case 0:
        m_description->setText("Base preset for an adult male body model.");
        break;
    case 1:
        m_description->setText("Base preset for an adult female body model.");
        break;
    default:
        m_description->setText("Neutral preset for early prototyping and shared testing.");
        break;
    }
}
