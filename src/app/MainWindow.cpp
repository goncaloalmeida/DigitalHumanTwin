#include "MainWindow.h"

#include <QHBoxLayout>
#include <QLabel>
#include <QListWidget>
#include <QStackedWidget>
#include <QWidget>

MainWindow::MainWindow(QWidget* parent)
    : QMainWindow(parent) {
    buildShell();
}

void MainWindow::setModuleManager(ModuleManager* manager) {
    m_moduleManager = manager;
    refreshModules();
}

void MainWindow::buildShell() {
    auto* root = new QWidget(this);
    auto* layout = new QHBoxLayout(root);

    m_navigation = new QListWidget(root);
    m_navigation->setMinimumWidth(220);

    m_stack = new QStackedWidget(root);
    m_emptyState = new QLabel("Base application ready. Add future features under src/modules.", root);
    m_emptyState->setWordWrap(true);
    m_emptyState->setAlignment(Qt::AlignCenter);

    m_stack->addWidget(m_emptyState);

    layout->addWidget(m_navigation);
    layout->addWidget(m_stack, 1);

    setCentralWidget(root);
    setWindowTitle("Digital Human Twin");
    resize(1100, 700);

    connect(m_navigation, &QListWidget::currentRowChanged, this, [this](int index) {
        if (index < 0) {
            m_stack->setCurrentIndex(0);
            return;
        }

        m_stack->setCurrentIndex(index + 1);
    });
}

void MainWindow::refreshModules() {
    m_navigation->clear();

    while (m_stack->count() > 1) {
        auto* widget = m_stack->widget(1);
        m_stack->removeWidget(widget);
        widget->deleteLater();
    }

    if (m_moduleManager == nullptr || m_moduleManager->modules().empty()) {
        m_navigation->setCurrentRow(-1);
        m_stack->setCurrentIndex(0);
        return;
    }

    for (const auto& module : m_moduleManager->modules()) {
        m_navigation->addItem(module->displayName());
        m_stack->addWidget(module->view());
    }

    m_navigation->setCurrentRow(0);
}
