#pragma once

#include <QString>

class QWidget;

class IModule {
public:
    virtual ~IModule() = default;

    virtual QString id() const = 0;
    virtual QString displayName() const = 0;
    virtual QWidget* view() = 0;
    virtual void initialize() {}
};
