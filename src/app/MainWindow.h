#pragma once

#include "core/ModuleManager.h"

#include <QMainWindow>

class QListWidget;
class QStackedWidget;
class QLabel;

class MainWindow : public QMainWindow {
    Q_OBJECT

public:
    explicit MainWindow(QWidget* parent = nullptr);
    void setModuleManager(ModuleManager* manager);

private:
    void buildShell();
    void refreshModules();

    ModuleManager* m_moduleManager = nullptr;
    QListWidget* m_navigation = nullptr;
    QStackedWidget* m_stack = nullptr;
    QLabel* m_emptyState = nullptr;
};
