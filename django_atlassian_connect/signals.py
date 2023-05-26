from django import dispatch

lifecycle_installed = dispatch.Signal()
lifecycle_enabled = dispatch.Signal()
lifecycle_disabled = dispatch.Signal()
lifecycle_uninstalled = dispatch.Signal()
