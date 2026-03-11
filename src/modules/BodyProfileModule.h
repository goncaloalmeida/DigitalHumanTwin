#pragma once

#include "core/IModule.h"

class QLabel;
class QComboBox;
class QWidget;

class BodyProfileModule : public IModule {
public:
    BodyProfileModule();

    QString id() const override;
    QString displayName() const override;
    QWidget* view() override;
    void initialize() override;

private:
    void buildView();
    void updateDescription(int index);

    QWidget* m_root = nullptr;
    QComboBox* m_bodyType = nullptr;
    QLabel* m_description = nullptr;
};
